<template>
  <v-dialog v-model="showNotification"
            :persistent="!showGuessResult"
            max-width="600"
            overlay-opacity="0.1">
    <v-card min-height="300">
      <v-fade-transition>
        <v-overlay :value="showGuessResult" absolute opacity="0">
          <v-container v-if="matchGuessResult">
            <v-row align="center" justify="center">
              <v-icon x-large color="green">done</v-icon>
            </v-row>
            <v-row align="center" justify="center">
              <p class="headline black--text">Correct!</p>
            </v-row>
            <v-row align="center" justify="center"
                   v-if="!doneGuessing">
              <p class="black--text">{{isGuessing ? "Guess again!" : guesserName + " guesses again"}}</p>
            </v-row>
          </v-container>
          <v-container v-else>
            <v-row align="center" justify="center">
              <v-icon size="200px" color="red">close</v-icon>
            </v-row>
            <v-row align="center" justify="center">
              <p class="black--text">{{isGuessing ? "Your" : guesserName+"'s"}} turn to guess</p>
            </v-row>
          </v-container>
        </v-overlay>
      </v-fade-transition>
      <v-card-title class="justify-center card-title-wrap">{{playerName}} guessed {{guessedPlayerName}} wrote</v-card-title>
      <v-card-text class="justify-center headline">{{guessedAnswer}}</v-card-text>
    </v-card>
  </v-dialog>
</template>

<script>
  import {mapGetters} from "vuex";

  export default {
    name: "MatchNotification",
    data: function() {
      return {
        showNotification: false,
        playerName: "",
        guessedPlayerName: "",
        guessedAnswer: "",
        showGuessResult: false,
        matchGuessResult: false,
      };
    },
    computed: {
      ...mapGetters(["thisPlayer", "currentGuesser", "otherGuessers", "gameState"]),
      isGuessing() {
        if (!this.thisPlayer || !this.currentGuesser) return false;
        return this.thisPlayer.id === this.currentGuesser.id;
      },
      guesserName() {
        return this.currentGuesser ? this.currentGuesser.name : "";
      },
      doneGuessing() {
        return this.gameState === "round_complete";
      }
    },
    sockets: {
      match_submitted: function(data) {
        const player = data.player;
        this.playerName = this.isGuessing ? "You" : player.name;
        this.guessedPlayerName = data.guessed_player.name;
        this.guessedAnswer = data.guessed_answer.text;
        this.matchGuessResult = null;
        this.showGuessResult = false;
        this.showNotification = true;
      },
      match_result: function(data) {
        this.matchGuessResult = data.result;
        this.showNotification = true;
        this.showGuessResult = true;
        setTimeout(() => {
          this.showNotification = false;
          this.showGuessResult = false;
        }, 2000);
      }
    },
  }
</script>

<style scoped>

</style>