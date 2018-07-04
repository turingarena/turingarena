const { merge } = require('@neutrinojs/compile-loader');

module.exports = {
  use: [
    '@neutrinojs/react',
    [
      '@neutrinojs/env', [
        'TURINGARENA_EVALUATE_ENDPOINT',
        'TURINGARENA_PROBLEM_URL',
      ]
    ],
    (neutrino) => neutrino.config.module
      .rule('compile')
      .use('babel')
      .tap(options => merge({
        plugins: [
          'babel-plugin-transform-decorators-legacy',
          'babel-plugin-transform-class-properties',
        ]
      }, options))
  ]
};
