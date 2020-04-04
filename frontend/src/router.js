import Vue from 'vue';
import Router from 'vue-router';
import Home from '@/views/Home';
import Game from '@/views/Game';

Vue.use(Router);

export default new Router({
  mode: 'history',
  routes: [
    {
      path: '/',
      name: 'Home',
      component: Home,
    },
    {
      path: '/:room',
      name: 'Game',
      component: Game,
    },
  ],
});