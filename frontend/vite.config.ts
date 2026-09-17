import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

const backendUrl = process.env.BACKEND_URL || "http://localhost:8000";

// Port 3000 matches CORS_ALLOWED_ORIGINS in backend/.env.example (see doc/05-local-development.md).
export default defineConfig({
	plugins: [react()],
	server: {
		host: "0.0.0.0",
		port: 3000,
		proxy: {
			"/api": {
				target: backendUrl,
				changeOrigin: true,
			},
			"/oidc": {
				target: backendUrl,
				changeOrigin: true,
				xfwd: true,
				headers: {
					"X-Forwarded-Host": "localhost:3000",
					"X-Forwarded-Proto": "http",
				},
			},
		},
	},
});

