<template>
  <v-container>
    <v-row v-for="p in game.players" :key="p.id">
      <player v-bind:player="p"></player>
    </v-row>
  </v-container>
</template>

<script>
  import Player from "../components/Player";
  import {mapState} from "vuex";

  export default {
    name: "Game",
    components: {
      Player,
    },
    computed: {
      ...mapState(['playerId', 'gameId', 'game'])
    },
  }
</script>

<style scoped>

</style>