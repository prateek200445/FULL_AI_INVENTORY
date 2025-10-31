import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

// ✅ Simple setup — no backend proxy
export default defineConfig({
  plugins: [react(), tailwindcss()],
});
