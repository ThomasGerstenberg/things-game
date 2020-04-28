<template>
  <v-menu offset-y>
    <template v-slot:activator="{on}">
      <v-btn :color="color" dark x-small fab v-on="on">
        <v-icon dark>palette</v-icon>
      </v-btn>
    </template>
    <v-color-picker
      v-model="hexColor"
      hide-canvas hide-inputs disabled
      show-swatches :swatches="hexColors">
    </v-color-picker>
  </v-menu>
</template>

<script>
  import {mapMutations, mapState} from "vuex";

  export default {
    name: "ColorPicker",
    data: function() {
      return {
        hexColor: "#000",
        colors: {
          "red": "#F44336",
          "pink": "#E91E63",
          "purple": "#9C27B0",
          "deep-purple": "#673AB7",
          "indigo": "#3F51B5",
          "blue": "#2196F3",
          "light-blue": "#03A9F4",
          "cyan": "#00BCD4",
          "teal": "#009688",
          "green": "#4CAF50",
          "light-green": "#8BC34A",
          "lime": "#CDDC39",
          "yellow": "#FFEB3B",
          "amber": "#FFC107",
          "orange": "#FF9800",
          "deep-orange": "#FF5722",
          "brown": "#795548",
          "blue-grey": "#607D8B",
          "grey": "#9E9E9E",
        },
      };
    },
    watch: {
      hexColor() {
        const color = Object.keys(this.colors).find(k => this.colors[k] === this.hexColor);
        this.setColor(color);
      },
      color() {
        this.updateColor(this.color);
      }
    },
    computed: {
      ...mapState(["color"]),
      hexColors() {
        var hexColors = Object.values(this.colors);
        return [hexColors.slice(0, hexColors.length/2), hexColors.slice(hexColors.length/2)];
      },
    },
    methods: {
      ...mapMutations(["setColor"]),
      updateColor(color) {
        this.hexColor = this.colors[color];
      }
    },
    mounted() {
      if (!this.color) {
        const colorNames = Object.keys(this.colors);
        const i = Math.floor(Math.random() * colorNames.length);
        this.setColor(colorNames[i]);
        this.updateColor(colorNames[i])
      }
      else
        this.updateColor(this.color)
    }
  }
</script>

<style scoped>

</style>