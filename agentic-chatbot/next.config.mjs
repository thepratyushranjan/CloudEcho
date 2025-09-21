/** @type {import('next').NextConfig} */
const nextConfig = {
  // Configure Next.js to bind to all interfaces (0.0.0.0) instead of localhost
  // This is required for Docker containers to be accessible from outside
  experimental: {
    serverComponentsExternalPackages: [],
  },
  // Ensure the server binds to 0.0.0.0
  env: {
    HOSTNAME: '0.0.0.0',
    PORT: '8079',
  },
};

export default nextConfig;
