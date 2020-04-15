<template>
  <v-dialog v-model="showDialog" persistent max-width="600">
    <v-card>
      <v-card-title class="card-title-wrap justify-center">Things {{topic}}
      </v-card-title>
      <v-card-text>
        <v-text-field v-model="answer"
                      @keypress.enter="submit"
                      required>
        </v-text-field>
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn color="primary darken-1" text @click="submit">Submit</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
  import {mapGetters, mapState} from "vuex";

  export default {
    name: "SubmitAnswer",
    data: function() {
      return {
        showDialog: false,
        answer: "",
      }
    },
    computed: {
      ...mapState(["gameId", "playerId", "sessionKey"]),
      ...mapGetters(["gameState", "thisPlayer", "topic"]),
    },
    watch: {
      gameState() {
        this.updateDialogState();
      },
      thisPlayer() {
        this.updateDialogState();
      }
    },
    methods: {
      updateDialogState() {
        this.showDialog = this.gameState === "writing_answers" && !this.thisPlayer.submitted_answer;
        if (!this.showDialog) this.answer = "";
      },
      submit() {
        if (this.answer) {
          const params = {
            game_id: this.gameId,
            player_id: this.playerId,
            session_key: this.sessionKey,
            answer: this.answer,
          };
          this.$socket.emit("submit_answer", params)
        }
      }
    },
    mounted() {
      this.updateDialogState();
    }
  }
</script>

<style scoped>

</style>