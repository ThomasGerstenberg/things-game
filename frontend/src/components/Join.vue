<template>
  <v-container>
    <v-row>
      <v-col cols="12" md="6" lg="4">
        <v-text-field
          prepend-icon="person_add"
          v-model="gameId"
          :rules="idRules"
          label="Game ID"
          autocomplete="off"
          @keypress.enter="joinGame"
          required>
        </v-text-field>
      </v-col>
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
      <v-btn color="primary" @click="joinGame">Join</v-btn>
    </v-row>
  </v-container>
</template>

<script>
  import {mapMutations, mapState} from "vuex";

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
    computed: {
      ...mapState(["color"]),
    },
    methods: {
      ...mapMutations(["setUsername"]),
      joinGame() {
        if (!this.username) return;
        this.setUsername(this.username);
        console.log("Joining game: " + this.gameId +
          ", Password: " + this.password +
          ", Username: " + this.username);
        const params = {
          game_id: this.gameId.toUpperCase(),
          player_name: this.username,
          color: this.color,
        };
        this.$socket.emit("join_game", params);
      }
    },
    mounted() {
      if (this.$route.query.gameId) {
        this.gameId = this.$route.query.gameId;
      }
    }
  }
</script>

<style scoped>

</style>