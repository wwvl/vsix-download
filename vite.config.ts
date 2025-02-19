import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";

import ui from "@nuxt/ui/vite";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    ui({
      ui: {
        colors: {
          primary: "green",
          neutral: "slate",
        },
      },
    }),
  ],
});
