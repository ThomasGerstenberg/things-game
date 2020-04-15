<template>
  <div>
    <v-menu bottom :disabled="otherPlayers.length === 0" class="mx-1">
      <template v-slot:activator="{on}">
        <v-btn outlined v-on="on" small>
          Remove
          <v-icon right>person</v-icon>
        </v-btn>
      </template>
      <v-list>
        <v-list-item v-for="p in otherPlayers" :key="p.id" @click="removePlayer(p)">
          <v-list-item-title>{{p.name}}</v-list-item-title>
        </v-list-item>
      </v-list>
    </v-menu>
    <v-btn outlined class="mx-1" small
            @click="resetPoints">
      Reset Points
    </v-btn>
    <v-btn outlined class="mx-1" small
           :disabled="!canStart"
           @click="startGame">
      Start Game
    </v-btn>
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