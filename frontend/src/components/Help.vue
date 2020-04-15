<template>
  <v-card>
    <v-card-title>
      Things...
    </v-card-title>
    <v-card-subtitle>How To Play</v-card-subtitle>
    <v-card-text>
      <p>
        <b>Things...</b> is a party game where everyone writes a response to a particular prompt,
        such as "Things... you shouldn't put in your mouth," and the players then try to guess which player wrote which response.
      </p>
      <p>
        Each round, one person will write a prompt for everyone to answer.
        Once the prompt is written, each person will submit their own response to the prompt.
        Once all responses are submitted, all responses are revealed and players take turns matching responses to players.
      </p>
      <p>
        The guesser will try to match one response to one player. If they are correct, they gain a point and get to guess again.
        Players whose responses have been guessed are eliminated from the round. Once the guesser makes an incorrect guess, the
        next player will now make their guesses. The last player standing gets an extra point for winning the round.
      </p>
      <p>
        Once the round completes, a new round begins with the next prompt writer.
      </p>
      <p>
        The game ends when you choose to (point total, time, etc.)
        The person who created the room can reset the points in order to start a new game
      </p>
    </v-card-text>
  </v-card>
</template>

<script>
  export default {
    name: "Help"
  }
</script>

<style scoped>

</style>