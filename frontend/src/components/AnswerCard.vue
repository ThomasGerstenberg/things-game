<template>
  <v-dialog v-model="showDialog" scrollable max-width="500" :disabled="!canSelectPlayer">
    <template v-slot:activator="{ on }">
    <v-hover v-slot:default="{hover}" :disabled="!canSelectPlayer">
        <v-card :elevation="hover ? 8 : 2" v-on="on">
          <v-card-text>{{answer.text}}</v-card-text>
          <v-card-actions>
            <player v-if="player" :player="player" :show-icons="false"></player>
          </v-card-actions>
        </v-card>
      </v-hover>
    </template>
    <v-card>
      <v-card-title>Who wrote '{{answer.text}}'?</v-card-title>
      <v-card-text>
        <v-list>
          <v-list-item
            v-for="p in otherGuessers" :key="p.id" @click="submitAnswer(p)">
            <v-list-item-icon>
              <v-icon :color="p.color">person</v-icon>
            </v-list-item-icon>
            <v-list-item-content>
              <v-list-item-title>{{p.name}}</v-list-item-title>
            </v-list-item-content>
          </v-list-item>
        </v-list>
      </v-card-text>
    </v-card>
  </v-dialog>
</template>

<script>
  import {mapGetters, mapMutations, mapState} from "vuex";
  import Player from "./Player";

  export default {
    name: "Answer.vue",
    props: ["answer"],
    components: {
      Player
    },
    data: function() {
      return {
        showDialog: false
      };
    },
    computed: {
      ...mapState(["gameId", "playerId", "sessionKey"]),
      ...mapGetters(["thisPlayer", "otherGuessers"]),
      canSelectPlayer() {
        return this.thisPlayer.is_guessing && !this.answer.player;
      },
      player() {
        return this.answer.player;
      },
    },
    methods: {
      ...mapMutations(["setMessage"]),
      submitAnswer(player) {
        const params = {
          game_id: this.gameId,
          player_id: this.playerId,
          session_key: this.sessionKey,
          guessed_player_id: player.id,
          answer_id: this.answer.id
        };
        this.$socket.emit("submit_match", params);
        this.setMessage("Submitting Answer...");
        this.showDialog = false;
      }
    }
  }
</script>

<style scoped>

</style>