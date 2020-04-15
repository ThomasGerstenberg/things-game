import threading
import time
from typing import List
import logging


logger = logging.getLogger(__name__)


class _Task(object):
    @property
    def expired(self):
        return NotImplementedError

    @property
    def should_remove(self):
        return NotImplementedError

    def execute(self):
        return NotImplementedError


class _SingleShotTask(_Task):
    def __init__(self, scheduled_time, action, args, kwargs):
        self.scheduled_time = scheduled_time
        self.action = action
        self.args = args
        self.kwargs = kwargs
        self.executed = False

    @property
    def expired(self):
        return time.time() >= self.scheduled_time

    @property
    def should_remove(self):
        return self.executed

    def execute(self):
        self.action(*self.args, **self.kwargs)
        self.executed = True


class _PeriodicTask(_Task):
    def __init__(self, period, action, args, kwargs):
        self.period = period
        self.action = action
        self.args = args
        self.kwargs = kwargs
        self.last_run_time = time.time()
        self.cancelled = False

    @property
    def expired(self):
        return (time.time() - self.last_run_time) > self.period

    @property
    def should_remove(self):
        return self.cancelled

    def execute(self):
        self.action(*self.args, **self.kwargs)
        self.last_run_time = time.time()

    def cancel(self):
        self.cancelled = True


class BackgroundTaskScheduler(object):
    def __init__(self, tick_interval=0.5):
        self.thread = threading.Thread(target=self.run, daemon=True)
        self.lock = threading.Lock()
        self.tick_interval = tick_interval
        self.tasks: List[_Task] = []
        self.stop_event = threading.Event()

    def run_in(self, time_seconds, task, *args, **kwargs):
        task = _SingleShotTask(time.time() + time_seconds, task, args, kwargs)
        with self.lock:
            self.tasks.append(task)

    def run_every(self, time_seconds, task, *args, **kwargs):
        task = _PeriodicTask(time_seconds, task, args, kwargs)
        with self.lock:
            self.tasks.append(task)

    def start(self):
        self.thread.start()

    def stop(self):
        self.stop_event.set()
        self.thread.join(self.tick_interval*4)

    def run(self):
        # Very primitive, could be made much better
        while not self.stop_event.is_set():
            time.sleep(self.tick_interval)
            tasks_to_remove = []
            with self.lock:
                tasks_to_check = self.tasks[:]
            for task in tasks_to_check:
                if task.expired:
                    try:
                        task.execute()
                    except Exception as e:
                        logger.exception(e)
                if task.should_remove:
                    tasks_to_remove.append(task)
            with self.lock:
                for task in tasks_to_remove:
                    self.tasks.remove(task)
