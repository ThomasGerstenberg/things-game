<template>
  <div>
    <v-menu bottom :close-on-content-click="false">
      <template v-slot:activator="{on}">
        <v-btn v-on="on" tile icon>
          <v-icon>settings</v-icon>
        </v-btn>
      </template>
      <v-list>
        <v-list-item :disabled="!canStart" @click="startGame">
          <v-list-item-title>Start Game</v-list-item-title>
        </v-list-item>
        <v-list-item @click="resetPoints">
          <v-list-item-title>Reset Points</v-list-item-title>
        </v-list-item>
        <v-list-item>
          <v-menu bottom :disabled="otherPlayers.length === 0">
            <template v-slot:activator="{on}">
              <v-list-item v-on="on">
                <v-list-item-title>
                  Remove Player
                </v-list-item-title>
              </v-list-item>
            </template>
            <v-list>
              <v-list-item v-for="p in otherPlayers" :key="p.id" @click="removePlayer(p)">
                <v-list-item-title>{{p.name}}</v-list-item-title>
              </v-list-item>
            </v-list>
          </v-menu>
        </v-list-item>
      </v-list>
    </v-menu>
  </div>
</template>

<script>
  import {mapGetters, mapState} from "vuex";

  export default {
    name: "GameAdmin",
    computed: {
      ...mapState(["game", "gameId", "playerId", "sessionKey"]),
      ...mapGetters(["gameState", "thisPlayer", "otherPlayers"]),
      canStart() {
        return this.game.players.length >= 3 && this.gameState === "not_started";
      }
    },
    methods: {
      startGame() {
        if (!this.canStart) return;

        const params = {
          game_id: this.gameId,
          player_id: this.playerId,
          session_key: this.sessionKey,
        };
        this.$socket.emit("start_game", params)
      },
      removePlayer(player) {
        console.log("Removing player " + player.name);
        this.$socket.emit("remove_player", {
          game_id: this.gameId,
          player_id: this.playerId,
          session_key: this.sessionKey,
          player_id_to_remove: player.id
        });
      },
      resetPoints() {
        this.$socket.emit("reset_points", {
          game_id: this.gameId,
          player_id: this.playerId,
          session_key: this.sessionKey,
        });
      }
    }
  }
</script>

<style scoped>

</style>