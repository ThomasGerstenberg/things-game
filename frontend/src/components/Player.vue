<template>
  <v-chip :color="player.color" dark>
    <div class="mr-1">{{player.name}}</div>
    <v-tooltip bottom v-if="player.is_topic_writer">
      <template v-slot:activator="{ on }">
        <v-icon v-on="on">edit</v-icon>
      </template>
      <span>{{player.name}} is the topic writer</span>
    </v-tooltip>
    <v-tooltip bottom v-if="player.submitted_answer">
      <template v-slot:activator="{on}">
        <v-icon v-on="on">done</v-icon>
      </template>
      <span>{{player.name}} submitted their answer</span>
    </v-tooltip>
    <v-avatar right :color="player.color" class="darken-1">
      {{player.score}}
    </v-avatar>
  </v-chip>
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