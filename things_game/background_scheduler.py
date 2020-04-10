import threading
import time
from typing import List


class _Task(object):
    def __init__(self, scheduled_time, action, args, kwargs):
        self.scheduled_time = scheduled_time
        self.action = action
        self.args = args
        self.kwargs = kwargs
        self.executed = False

    def execute(self):
        self.action(*self.args, **self.kwargs)
        self.executed = True

    @property
    def expired(self):
        return time.time() >= self.scheduled_time


class BackgroundTaskScheduler(object):
    def __init__(self, tick_interval=0.5):
        self.thread = threading.Thread(target=self.run, daemon=True)
        self.lock = threading.Lock()
        self.tick_interval = tick_interval
        self.tasks: List[_Task] = []
        self.stop_event = threading.Event()

    def run_in(self, time_seconds, task, *args, **kwargs):
        task = _Task(time.time()+time_seconds, task, args, kwargs)
        with self.lock:
            self.tasks.append(task)

    def start(self):
        self.thread.start()

    def stop(self):
        self.stop_event.set()
        self.thread.join(self.tick_interval*4)

    def run(self):
        while not self.stop_event.is_set():
            time.sleep(self.tick_interval)
            tasks_executed = []
            with self.lock:
                tasks_to_check = self.tasks[:]
            for task in tasks_to_check:
                if task.expired:
                    task.execute()
                    tasks_executed.append(task)
                elif task.executed:
                    tasks_executed.append(task)
            with self.lock:
                for task in tasks_executed:
                    self.tasks.remove(task)
