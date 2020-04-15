<template>
  <v-container v-if="game">
    <create-topic/>
    <submit-answer/>
    <match-notification/>
    <round-complete/>
    <v-container>
      <v-row class="mt-0">
        <p class="headline">Players</p>
      </v-row>
      <v-row>
        <v-col cols="auto" v-for="p in players" :key="p.id" class="mx-0">
          <player v-bind:player="p" :show-icons="true" class="mx-0"/>
        </v-col>
      </v-row>
    </v-container>
    <v-row v-if="topic">
      <p class="headline mx-4 mt-1">
        Things... {{topic}}
      </p>
    </v-row>
    <v-row v-if="gameState==='writing_topic' && !!topicWriter"
           justify="center">
      <player :player="topicWriter" :show-icons="false"/>
      <p class="headline ml-1">is writing the topic...</p>
    </v-row>
    <v-row v-if="gameState==='writing_answers'"
           justify="center">
      <p class="headline">Waiting for players to answer...</p>
    </v-row>
    <v-row>
      <v-col v-for="a in game.answers" cols="auto" :key="a.id">
        <answer-card v-bind:answer="a" />
      </v-col>
    </v-row>
    <v-row v-if="gameState === 'matching' && currentGuesser" justify="center">
      <player :player="currentGuesser" :show-icons="false"/>
      <p class="headline ml-1">is guessing...</p>
    </v-row>
  </v-container>
</template>

<script>
  import Player from "../components/Player";
  import {mapGetters, mapState} from "vuex";
  import CreateTopic from "../components/CreateTopic";
  import SubmitAnswer from "../components/SubmitAnswer";
  import AnswerCard from "../components/AnswerCard";
  import MatchNotification from "../components/MatchNotification";
  import RoundComplete from "../components/RoundComplete";

  export default {
    name: "Game",
    components: {
      MatchNotification,
      SubmitAnswer,
      CreateTopic,
      Player,
      AnswerCard,
      RoundComplete,
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
      ...mapGetters(["topic", "gameState", "thisPlayer", "currentGuesser", "topicWriter", "players"]),
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