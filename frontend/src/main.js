import Vue from 'vue'
import VueSocketIO   from 'vue-socket.io';
import Vuetify from "vuetify";
import VueResizeText from 'vue-resize-text';
import io from "socket.io-client";
import { sync } from 'vuex-router-sync'

import App from './App.vue';
import store from './store';
import router from "./router";
import vuetify from './plugins/vuetify';
import 'material-design-icons-iconfont/dist/material-design-icons.css';
import './assets/css/global.css';


const connection = io.connect("http://" + window.location.host);

Vue.config.productionTip = false;

Vue.use(new VueSocketIO({
  connection: connection,
  debug: true,
  vuex: {
    store,
    actionPrefix: "SOCKET_",
    mutationPrefix: "SOCKET_"
  }
}), store);
Vue.use(Vuetify);
Vue.use(VueResizeText);

new Vue({
  router,
  store,
  render: h => h(App),
  vuetify,

  beforeCreate () {
    // before creating vue app, check if current path doesn't match stored path
    // check if store contains a route first
    if (this.$store.state.route && (this.$route.path !== this.$store.state.route.path)) {
      this.$router.push(this.$store.state.route.path)
    }
    // vue router sync with vuex
    sync(store, router) // done. Returns an unsync callback fn
  }
}).$mount('#app');
