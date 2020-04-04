<template>
  <v-card elevation="12" class="px-4">
    <v-row>
      <v-col align="center"
        sm="12" md="6" lg="4" xl="4">
        <v-text-field
          prepend-icon="person"
          v-model="username"
          :rules="nameRules"
          label="Username"
          required>
        </v-text-field>
      </v-col>
    </v-row>
    <v-divider/>
    <v-row>
      <v-col lg="6" xs="12" sm="12">
        <v-card outlined tile class="pa-2">
          <v-card-title class="text-no-wrap">Create Game</v-card-title>
          <create v-bind:username="username"/>
        </v-card>
      </v-col>
      <v-col lg="6" xs="12" sm="12">
        <v-card outlined tile class="pa-2">
          <v-card-title class="text-no-wrap">Join Game</v-card-title>
          <join v-bind:username="username"/>
        </v-card>
      </v-col>
    </v-row>
  </v-card>
</template>

<script>
  import Join from "../components/Join";
  import Create from "../components/Create";
  import {mapState} from "vuex";

  export default {
    name: 'Home',
    components: {
      Create,
      Join,
    },
    computed: {
      ...mapState(['playerId', 'gameId'])
    },
    watch: {
      playerId() {
        this.$router.push({name: "Game", params: {room: this.gameId}});
      }
    },
    data: function() {
      return {
        username: '',
        nameRules: [
          v => !!v || "Must enter a name",
        ]
      }
    }
  }
</script>
