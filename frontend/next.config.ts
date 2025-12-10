import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  allowedDevOrigins: [
    "local-origin.dev",
    "*.local-origin.dev",
    "128.226.206.249",
  ],
  async redirects() {
    return [
      {
        source: "/",
        destination: "/chan",
        permanent: false,
      },
    ];
  },
};

export default nextConfig;
