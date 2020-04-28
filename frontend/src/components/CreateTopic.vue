<template>
  <v-dialog v-model="showDialog" persistent max-width="600">
    <v-card>
      <v-card-title class="headline">
        Your Turn! Write your topic
      </v-card-title>
      <v-card-text>
        <v-text-field label="Things..."
                      v-model="topic"
                      @keypress.enter="submit"
                      ref="topicInput"
                      autocomplete="off"
                      required>
        </v-text-field>
      </v-card-text>
      <v-card-actions>
        <v-tooltip bottom v-if="showHelp">
          <template v-slot:activator="{on}">
            <v-btn color="primary" text x-small
                   v-on="on"
                   @click="requestTopic">
              Need Inspiration?
            </v-btn>
          </template>
          <span>Click here for a topic suggestion</span>
        </v-tooltip>
        <v-spacer />
        <v-btn color="primary darken-1" text @click="submit">Submit</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
  import {mapGetters, mapState} from "vuex";

  export default {
    name: "CreateTopic",
    data: function() {
      return {
        topic: '',
        showDialog: false,
        showHelp: false,
      };
    },
    computed: {
      ...mapState(["gameId", "playerId", "sessionKey"]),
      ...mapGetters(["gameState", "thisPlayer"]),
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
        this.showDialog = this.gameState === "writing_topic" && this.thisPlayer.is_topic_writer;
        if (!this.showDialog) {
          this.topic = "";
        }
        else {
          requestAnimationFrame(() => this.$refs.topicInput.focus());
        }
      },
      submit() {
        if (this.topic) {
          const params = {
            game_id: this.gameId,
            player_id: this.playerId,
            session_key: this.sessionKey,
            topic: this.topic,
          };
          this.$socket.emit("set_topic", params);
        }
      },
      requestTopic() {
        this.$socket.emit("get_random_topic")
      }
    },
    sockets: {
      random_topic: function(data) {
        this.showHelp = false;
        this.topic = data.text;
      }
    },
    mounted() {
      this.updateDialogState();
      this.showHelp = false;
      setTimeout(() => this.showHelp = true, 20000);
    }
  }
</script>

<style scoped>

</style>