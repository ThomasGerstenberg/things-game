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
           class="theme--dark grey--text text--lighten-4 body-2">
        ID: {{gameId}}
        <v-btn tile icon x-small
               @click="copyInvite">
          <v-icon class="grey--text text--lighten-4 mr-2">mdi-content-copy</v-icon>
        </v-btn>
      </div>
      <color-picker v-if="inGame" class=""/>
      <game-admin v-if="inGame && thisPlayer && thisPlayer.is_owner" class=""/>

      <v-btn v-if="inGame" @click="leaveGame" tile icon>
        <v-icon>mdi-logout</v-icon>
      </v-btn>
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
    <notification/>
  </v-app>
</template>

<script>
  import {mapGetters, mapMutations, mapState} from "vuex";
  import GameAdmin from "./components/GameAdmin";
  import Help from "./components/Help";
  import ColorPicker from "./components/ColorPicker";
  import Notification from "./components/Notification";
  export default {
    name: 'App',
    components: {
      Notification,
      ColorPicker,
      Help,
      GameAdmin
    },
    data: () => ({
    }),
    watch: {
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
      ...mapState(["gameId", "playerId", "sessionKey", "error", "color"]),
      ...mapGetters(["thisPlayer", "inGame"])
    },
    methods: {
      ...mapMutations(["setMessage"]),
      leaveGame() {
        this.$router.push("/");
      },
      copyInvite() {
        var inviteUrl = window.location.origin + "/?gameId=" + this.gameId;
        this.$copyText(inviteUrl).then(
          () => this.setMessage("Invite link copied to clipboard"),
          () => this.setMessage("Failed to copy invite link to clipboard")
        );
      },
    },
    mounted() {
      // Clear any leftover messages
      this.setMessage("");
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