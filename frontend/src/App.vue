<template>
  <v-app>
    <v-app-bar
      app
      color="primary"
      dark>
      <div class="d-flex align-center">
        <v-toolbar-title class="headline text-lowercase">Things...</v-toolbar-title>
      </div>

      <v-spacer></v-spacer>
      <game-admin v-if="inGame && thisPlayer && thisPlayer.is_owner"/>

      <v-btn v-if="inGame" @click="leaveGame" outlined class="mx-1">Leave Game</v-btn>
    </v-app-bar>

    <v-content>
      <v-container>
        <v-row align="center" justify="center">
          <v-col cols="12" lg="8" xl="6">
            <router-view/>
          </v-col>
        </v-row>
      </v-container>
    </v-content>
    <v-snackbar :timeout="3000" v-model="showSnackbar">
      {{message}}
    </v-snackbar>
  </v-app>
</template>

<script>
  import GameAdmin from "./components/GameAdmin";
  import {mapGetters, mapState} from "vuex";
  export default {
    name: 'App',
    components: {
      GameAdmin
    },
    data: () => ({
      showSnackbar: false,
      showError: false,
    }),
    watch: {
      message() {
        this.showSnackbar = !!this.message;
      },
      error() {
        this.showError = !!this.error;
      }
    },
    computed: {
      ...mapState(["gameId", "playerId", "sessionKey", "message", "error"]),
      ...mapGetters(["thisPlayer", "inGame"])
    },
    methods: {
      leaveGame() {
        const params = {
          game_id: this.gameId,
          player_id: this.playerId,
          session_key: this.sessionKey,
        };
        this.$socket.emit("leave_game", params);
        this.$router.push("/");
      }
    },
    mounted() {
      if (!this.gameId)
        return;
      const params = {
        game_id: this.gameId,
        player_id: this.playerId,
        sessionKey: this.sessionKey,
      };
      this.$socket.emit("request_update", params);
    }
  };
</script>
