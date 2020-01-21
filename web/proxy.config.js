/** @type { import('webpack-dev-server').ProxyConfigArray } */
const config = [
  {
    context: ['/graphql', '/files'],
    target: 'http://localhost:3000',
    secure: false,
    logLevel: 'debug',
    changeOrigin: true,
  },
];

module.exports = config;
