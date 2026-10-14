import type { NextConfig } from "next";

const backendUrl = process.env.INTERNAL_API_URL ?? process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

const nextConfig: NextConfig = {
  async rewrites() {
    return [{ source: "/backend-api/:path*", destination: `${backendUrl}/api/:path*` }];
  },
};

export default nextConfig;
