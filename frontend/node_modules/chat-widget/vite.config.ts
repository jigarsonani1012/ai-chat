import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { resolve } from "path";

export default defineConfig({
  plugins: [react()],
  build: {
    lib: {
      entry: resolve(__dirname, "src/embed.tsx"),
      name: "AiChatbotWidget",
      fileName: () => "widget.js",
      formats: ["iife"],
    },
  },
});
