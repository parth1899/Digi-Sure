import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";
import path from "path";
import dotenv from "dotenv";

// Load the .env file from the root (one level above /Frontend)
dotenv.config({ path: path.resolve(__dirname, "../.env") });

export default defineConfig({
  plugins: [react(), tailwindcss()],
  define: {
    "import.meta.env": {
      VITE_EMAILJS_SERVICE_ID: JSON.stringify(
        process.env.VITE_EMAILJS_SERVICE_ID
      ),
      VITE_EMAILJS_TEMPLATE_ID: JSON.stringify(
        process.env.VITE_EMAILJS_TEMPLATE_ID
      ),
      VITE_EMAILJS_PUBLIC_KEY: JSON.stringify(
        process.env.VITE_EMAILJS_PUBLIC_KEY
      ),
    },
  },
});
