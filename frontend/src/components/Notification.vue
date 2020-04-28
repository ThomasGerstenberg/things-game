<template>
    <v-snackbar :timeout="3000" v-model="showNotification" @input="onSnackbarChanged">
      {{notificationText}}
    </v-snackbar>
</template>

<script>
  import {mapMutations, mapState} from "vuex";

  export default {
    name: "Notification",
    data: () => ({
      showNotification: false,
      notificationText: "",
      notificationQueue: [],
    }),
    watch: {
      message() {
        if (this.message === "") return;
        const message = this.message;
        this.setMessage("");

        if (this.showNotification){
          if (!this.notificationQueue.includes(message))
            this.notificationQueue.push(message);
        }
        else {
          this.notificationText = message;
          this.showNotification = true;
        }
      }
    },
    computed: {
      ...mapState(["message"])
    },
    methods: {
      ...mapMutations(["setMessage"]),
      onSnackbarChanged(newState) {
        if (newState) return;

        const message = this.notificationQueue.shift()
        if (message !== undefined && message !== null && message !== "") {
          setTimeout(() => {
            this.notificationText = message;
            this.showNotification = true;
          }, 10);
        }
      }
    }

  }
</script>

<style scoped>

</style>