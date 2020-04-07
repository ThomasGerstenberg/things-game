<template>
  <v-btn outlined
     :disabled="!canStart"
      @click="startGame">
    Start Game
  </v-btn>
</template>

<script>
  import {mapState} from "vuex";

  export default {
    name: "GameAdmin",
    computed: {
      ...mapState(["game", "gameId", "playerId", "sessionKey"]),
      canStart() {
        return this.game.players.length >= 3;
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