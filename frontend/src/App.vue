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
      <div v-if="gameId"
           class="theme--dark px-2 grey--text text--lighten-4">
        Game ID: {{gameId}}
      </div>
      <color-picker v-if="inGame" class="mx-4"/>
      <game-admin v-if="inGame && thisPlayer && thisPlayer.is_owner" class="mx-2"/>

      <v-btn v-if="inGame" @click="leaveGame" outlined class="mx-1" small>Leave Game</v-btn>
      <v-dialog max-width="600" scrollable>
        <template v-slot:activator="{on}">
          <v-btn tile icon v-on="on" large>
            <v-icon>help</v-icon>
          </v-btn>
        </template>
        <help></help>
      </v-dialog>
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
  import {mapGetters, mapMutations, mapState} from "vuex";
  import GameAdmin from "./components/GameAdmin";
  import Help from "./components/Help";
  import ColorPicker from "./components/ColorPicker";
  export default {
    name: 'App',
    components: {
      ColorPicker,
      Help,
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
      },
      color() {
        if (!this.inGame)
          return;
        this.$socket.emit("change_color", {
          game_id: this.gameId,
          player_id: this.playerId,
          session_key: this.sessionKey,
          color: this.color,
        });
        this.setMessage("Color should take effect on next game update")
      }
    },
    computed: {
      ...mapState(["gameId", "playerId", "sessionKey", "message", "error", "color"]),
      ...mapGetters(["thisPlayer", "inGame"])
    },
    methods: {
      ...mapMutations(["setMessage"]),
      leaveGame() {
        this.$router.push("/");
      }
    },
    mounted() {
      if (!this.gameId)
        return;
      const params = {
        game_id: this.gameId,
        player_id: this.playerId,
        session_key: this.sessionKey,
      };
      this.$socket.emit("request_update", params);
    }
  };
</script>

<style>

</style>