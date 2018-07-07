const { merge } = require('@neutrinojs/compile-loader');

module.exports = {
  use: [
    (neutrino) => neutrino.config.module
      .rule('compile')
      .use('babel')
      .tap(options => merge({
        plugins: [
          require.resolve('babel-plugin-transform-async-generator-functions'),
          require.resolve('babel-plugin-transform-decorators-legacy'),
          require.resolve('babel-plugin-transform-class-properties'),
        ]
      }, options)),
  ]
};
