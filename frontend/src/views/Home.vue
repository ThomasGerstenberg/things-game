<template>
  <v-card elevation="12" class="px-4">
    <v-row>
      <v-col cols="auto">
        <v-text-field
          prepend-icon="person"
          v-model="username"
          :rules="nameRules"
          label="Username"
          required>
        </v-text-field>
      </v-col>
      <v-col cols="auto" class="mt-2">
        <color-picker/>
      </v-col>
    </v-row>
    <v-divider/>
    <v-container>
      <v-row>
        <v-col md="6" xs="12">
          <v-card outlined tile class="pa-2">
            <v-card-title class="text-no-wrap">Create Game</v-card-title>
            <create v-bind:username="username"/>
          </v-card>
        </v-col>
        <v-col md="6" xs="12">
          <v-card outlined tile class="pa-2">
            <v-card-title class="text-no-wrap">Join Game</v-card-title>
            <join v-bind:username="username"/>
          </v-card>
        </v-col>
      </v-row>
    </v-container>
  </v-card>
</template>

<script>
  import Join from "../components/Join";
  import Create from "../components/Create";
  import {mapMutations, mapState} from "vuex";
  import ColorPicker from "../components/ColorPicker";

  export default {
    name: 'Home',
    components: {
      ColorPicker,
      Create,
      Join,
    },
    computed: {
      ...mapState(['playerId', 'gameId'])
    },
    watch: {
      playerId() {
        if (this.gameId) {
          this.$router.push({name: "Game", params: {room: this.gameId}});
        }
      }
    },
    data: function() {
      return {
        username: '',
        nameRules: [
          v => !!v || "Must enter a name",
        ]
      }
    },
    methods: {
      ...mapMutations(['reset'])
    },
    mounted() {
      this.username = this.$store.state.username;
      this.reset();
    }
  }
</script>
