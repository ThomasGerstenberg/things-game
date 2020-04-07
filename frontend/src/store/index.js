import Vue from 'vue';
import Vuex from 'vuex';
import createPersistedState from 'vuex-persistedstate';
import Cookies from 'js-cookie';

Vue.use(Vuex);

function inFifteenMinutes() { return new Date(new Date().getTime() + 15 * 60 * 1000);}


export default new Vuex.Store({
  plugins: [createPersistedState({
    storage: {
      getItem: key => Cookies.get(key),
      setItem: (key, value) => Cookies.set(key, value, { expires: inFifteenMinutes()}),
      removeItem: key => Cookies.remove(key)
    }
  })],
  state: {
    isConnected: false,
    username: '',
    gameId: '',
    playerId: '',
    sessionKey: '',
    game: null,
    error: null,
    message: '',
    color: 'blue',
  },

  getters: {
    thisPlayer(state) {
      if (state.game) {
        console.log(state.game);
        return state.game.players.find(p => p.id === state.playerId);
      }

      return undefined;
    },
    inGame(state) {
      return state.gameId !== "" && state.playerId !== "";
    },
    topic(state) {
      if (!state.game) return "";
      return state.game.current_topic.charAt(0).toLowerCase() + state.game.current_topic.slice(1);
    },
    gameState(state) {
      return state.game ? state.game.state : "";
    },
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
      state.game = message.game;
      state.gameId = message.game.game_id;
      if (state.playerId !== message.player.id)
        state.message = message.player.name + " joined the game";
    },

    SOCKET_player_left(state, message) {
      state.game = message.game;
      state.message = message.player.name + " left the game";
    },

    SOCKET_player_id(state, message) {
      state.playerId = message.player_id;
      state.sessionKey = message.session_key;
    },

    SOCKET_game_started(state, message) {
      state.game = message.game;
      state.message = "Game has started!"
    },

    SOCKET_topic_set(state, message) {
      state.game = message.game;
      state.message = "Topic has been set!"
    },

    SOCKET_answer_submitted(state, message) {
      state.game = message.game;
    },

    SOCKET_error(state, message) {
        state.error = message
    },

    SOCKET_game_update(state, message) {
      if (!message.game) {
        console.log("Resetting State");
        state.playerId = '';
        state.gameId = '';
        state.game = null;
        state.sessionKey = null;
        state.message = '';
        state.error = '';
      }
      else {
        this.game = message.game;
      }
    },

    setUsername(state, username) {
      state.username = username;
    },

    setColor(state, color) {
      state.color = color;
    },

    reset(state) {
      console.log("Resetting State");
      state.playerId = '';
      state.gameId = '';
      state.game = null;
      state.sessionKey = null;
      state.message = '';
      state.error = '';
    }
  }
})