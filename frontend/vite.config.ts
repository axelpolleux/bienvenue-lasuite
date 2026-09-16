import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

// Port 3000 matches CORS_ALLOWED_ORIGINS in backend/.env.example (see doc/05-local-development.md).
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
  },
});
