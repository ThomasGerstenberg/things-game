<template>
  <v-dialog v-model="showDialog"
            overlay-opacity="0.1"
            max-width="600">
    <v-card min-height="300">
      <v-card-title class="justify-center">
        Round Complete
      </v-card-title>
      <v-card-text class="text-center card-title-wrap">
        <p v-if="thisPlayerWon" class="headline">You won the round!</p>
        <span v-else>
          <player :player="winner" :show-icons="false"/>
          <p class="headline ml-1">won the round!</p>
        </span>
      </v-card-text>
    </v-card>
  </v-dialog>
</template>

<script>
  import Player from "./Player";
  import {mapGetters} from "vuex";

  export default {
    name: "RoundComplete",
    components: {
      Player,
    },
    data: function() {
      return {
        showDialog: false,
        winner: null,
      }
    },
    computed: {
      ...mapGetters(["thisPlayer"]),
      thisPlayerWon() {
        if (!this.thisPlayer || ! this.winner) return false;
        return this.thisPlayer.id === this.winner.id;
      }
    },
    sockets: {
      round_complete: function(data) {
        this.winner = data.winner;
        this.showDialog = true;
        setTimeout(() => this.showDialog = false, 15000);
      },
      round_started: function() {
        this.showDialog = false;
      }
    },
  }
</script>

<style scoped>

</style>