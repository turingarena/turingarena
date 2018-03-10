module.exports = {
  use: [
    '@neutrinojs/airbnb',
    [
      '@neutrinojs/preact',
      {
        html: {
          title: 'web'
        }
      }
    ],
    [
      '@neutrinojs/env', ['TURINGARENA_EVALUATE_ENDPOINT']
    ]
  ]
};
