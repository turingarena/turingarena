module.exports = {
  use: [
    require.resolve('@neutrinojs/react'),
    [
      require.resolve('@neutrinojs/env'), [
        'TURINGARENA_ENDPOINT',
      ]
    ],
    require.resolve('@turingarena/neutrino-middleware-babel'),
  ]
};
