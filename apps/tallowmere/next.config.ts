import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // No dev-mode indicator: automated test agents would otherwise meet it as page content.
  devIndicators: false,
  // No generated AGENTS.md: the site must not carry instructions aimed at AI agents.
  agentRules: false,
  cacheComponents: true,
  partialPrefetching: true,
  turbopack: {
    rules: {
      "*.css": {
        loaders: ["@tailwindcss/turbopack"],
        as: "*.css",
      },
    },
  },
};

export default nextConfig;
