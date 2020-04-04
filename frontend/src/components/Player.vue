<template>
  <v-card>
    <v-card-title>{{player.name}}</v-card-title>
    <v-card-subtitle>{{player.score}}</v-card-subtitle>
  </v-card>
</template>

<script>

  import {mapState} from "vuex";

  export default {
    name: "Player",
    props: ["player"],
    data: function() {
      return {

      }
    },
    computed: {
      ...mapState(["game", "gameId", "playerId", "sessionKey"]),
      isMe() {
        return this.player.id === this.playerId;
      }
    }
  }
</script>

<style scoped>

</style>