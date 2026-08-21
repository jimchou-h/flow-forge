import type { NextConfig } from "next";

/** 本地 Flask 默认地址；可用环境变量 FLOW_FORGE_API_ORIGIN 覆盖 */
const apiOrigin =
  process.env.FLOW_FORGE_API_ORIGIN ?? "http://127.0.0.1:5000";

const nextConfig: NextConfig = {
  async rewrites() {
    // 浏览器只请求同源 /api-proxy/*，由 Next 转发到 Flask，避免 CORS
    return [
      {
        source: "/api-proxy/:path*",
        destination: `${apiOrigin}/:path*`,
      },
    ];
  },
};

export default nextConfig;
