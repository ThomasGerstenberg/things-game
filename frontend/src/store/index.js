import Vue from 'vue';
import Vuex from 'vuex';

Vue.use(Vuex);

export default new Vuex.Store({
  state: {
    isConnected: false,
    username: '',
    gameId: '',
    playerId: '',
    sessionKey: '',
    game: {},
    error: null,
  },

  mutations: {
    SOCKET_CONNECT(state) {
      console.log("Connected");
      state.isConnected = true;
    },

    SOCKET_DISCONNECT(state) {
      console.log("Disconnected");
      state.isConnected = false;
    },

    SOCKET_player_joined(state, message) {
      console.log(message);
      state.game = message.game;
      state.gameId = message.game.game_id;
    },

    SOCKET_player_id(state, message) {
      console.log(message);
      state.playerId = message.player_id;
      state.sessionKey = message.session_key;
    },

    SOCKET_error(state, message) {
        state.error = message
    }
  }
})