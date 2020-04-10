<template>
  <v-btn outlined
     :disabled="!canStart"
      @click="startGame">
    Start Game
  </v-btn>
</template>

<script>
  import {mapGetters, mapState} from "vuex";

  export default {
    name: "GameAdmin",
    computed: {
      ...mapState(["game", "gameId", "playerId", "sessionKey"]),
      ...mapGetters(["gameState"]),
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
      }
    }
  }
</script>

<style scoped>

</style>