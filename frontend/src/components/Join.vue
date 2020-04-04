<template>
  <v-container>
    <v-row>
      <v-text-field
        prepend-icon="person_add"
        v-model="gameId"
        :rules="idRules"
        label="Game ID"
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
      <v-btn color="primary" @click="joinGame">Join</v-btn>
    </v-row>
  </v-container>
</template>

<script>
  export default {
    name: "Join",
    props: ["username"],
    data: function() {
      return {
        gameId: '',
        password: '',
        idRules: [
          v => !!v || "Must enter a game ID",
          v => v.length === 6 || "Game ID is 6 characters"
        ],
      }
    },
    methods: {
      joinGame() {
        console.log("Joining game: " + this.gameId +
          ", Password: " + this.password +
          ", Username: " + this.username);
        const params = {
          game_id: this.gameId.toUpperCase(),
          player_name: this.username,
        };
        this.$socket.emit("join_game", params);
      }
    }
  }
</script>

<style scoped>

</style>