<template>
  <v-container v-if="game">
    <create-topic/>
    <submit-answer/>
    <v-container>
      <v-row class="mt-0">
        <p class="headline">Players</p>
      </v-row>
      <v-row>
        <v-col cols="auto" v-for="p in game.players" :key="p.id" class="mx-0">
          <player v-bind:player="p" class="mx-0"/>
        </v-col>
      </v-row>
    </v-container>
    <v-row>
      <p class="headline mx-4 mt-1"
         v-if="topic">
        Things... {{topic}}
      </p>
    </v-row>
    <v-row>
      <v-col v-for="a in game.unguessed_answers" xs="12" lg="3" :key="a">
        <v-card>
          <v-card-text>{{a}}</v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
  import Player from "../components/Player";
  import {mapGetters, mapState} from "vuex";
  import CreateTopic from "../components/CreateTopic";
  import SubmitAnswer from "../components/SubmitAnswer";

  export default {
    name: "Game",
    components: {
      SubmitAnswer,
      CreateTopic,
      Player,
    },
    data: function() {
      return {
        showTopicDialog: false,
        showAnswerDialog: false,
      }
    },
    watch: {
      gameId() {
        if (!this.gameId) {
          this.$router.push("/");
        }
      }
    },
    computed: {
      ...mapState(['playerId', 'gameId', 'game']),
      ...mapGetters(["topic", "gameState", "thisPlayer"]),
    },
    mounted() {
      if (!this.gameId) {
        this.$router.push("/");
      }
    }
  }
</script>

<style scoped>

</style>