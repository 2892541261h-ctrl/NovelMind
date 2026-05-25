import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  // Base path for production build — assets are served from /assets/ by the
  // FastAPI backend, so relative paths break when loaded at /app/* routes.
  base: "/",
  server: {
    host: "127.0.0.1",
    port: 5173,
  },
});
