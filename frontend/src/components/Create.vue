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
    <v-row>
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
  export default {
    name: "Create",
    props: ["username"],
    data: function() {
      return {
        gameName: '',
        password: '',
        nameRules: [
          v => !!v || "Must enter a name",
          v => v.length > 5 || "Name must be > 5 characters"
        ],
      }
    },
    methods: {
      createGame () {
        console.log("Creating game: " + this.gameName +
          ", Password: " + this.password +
          ", Username: " + this.username);
        const params = {
          name: this.gameName,
          player_name: this.username,
        };
        this.$socket.emit("create_game", params);
      }
    }
  }
</script>

<style scoped>

</style>