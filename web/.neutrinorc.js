module.exports = {
  use: [
    '@neutrinojs/airbnb',
    '@neutrinojs/react',
    [
      '@neutrinojs/env', [
        'TURINGARENA_EVALUATE_ENDPOINT',
        'TURINGARENA_PROBLEM_URL',
      ]
    ]
  ]
};
