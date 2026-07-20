import type { NextConfig } from "next";

const pollingInterval = Number(process.env.CHOKIDAR_INTERVAL ?? 1000);
const usePolling = process.env.WATCHPACK_POLLING === "true";

const nextConfig: NextConfig = {};

if (usePolling) {
  nextConfig.webpack = (config, { dev }) => {
    if (dev) {
      config.watchOptions = {
        poll: pollingInterval,
        aggregateTimeout: 300,
        ignored: ["**/node_modules/**"],
      };
    }

    return config;
  };
}

export default nextConfig;
