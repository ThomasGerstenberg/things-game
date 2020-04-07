<template>
  <v-container>
    <v-row>
      <v-text-field
        prepend-icon="group_add"
        v-model="gameName"
        :rules="nameRules"
        label="Game Name"
        required>
      </v-text-field>
    </v-row>
    <v-row v-if="false">
      <v-text-field
        prepend-icon="lock"
        v-model="password"
        type="password"
        label="Password (optional)">
      </v-text-field>
    </v-row>
    <v-row>
      <v-btn color="primary" @click="createGame">Create</v-btn>
    </v-row>
  </v-container>
</template>

<script>
  import {mapMutations, mapState} from "vuex";

  export default {
    name: "Create",
    props: ["username"],
    data: function() {
      return {
        gameName: '',
        password: '',
        nameRules: [
          v => !!v || "Must enter a name",
        ],
      }
    },
    computed: {
      ...mapState(["color"]),
    },
    methods: {
      ...mapMutations(["setUsername"]),
      createGame () {
        this.setUsername(this.username);
        console.log("Creating game: " + this.gameName +
          ", Password: " + this.password +
          ", Username: " + this.username);
        const params = {
          name: this.gameName,
          player_name: this.username,
          color: this.color,
        };
        this.$socket.emit("create_game", params);
      }
    }
  }
</script>

<style scoped>

</style>