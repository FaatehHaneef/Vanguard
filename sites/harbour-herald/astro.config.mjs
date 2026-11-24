import { defineConfig } from "astro/config";

// A static site: `npm run build` writes dist/, which nginx serves on port 3106.
export default defineConfig({
  output: "static",
  trailingSlash: "ignore",
  build: { format: "directory" },
  server: { port: 3106, host: true },
  preview: { port: 3106, host: true },
  devToolbar: { enabled: false },
  telemetry: false,
});
