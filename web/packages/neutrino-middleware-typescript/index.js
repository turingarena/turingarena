module.exports = neutrino => neutrino.config.module
  .rule('compile-typescript')
  .test(/\.tsx?$/)
  .use('typescript')
  .loader(require.resolve('awesome-typescript-loader'))
  .options({
    module: "commonjs",
    lib: [
      "es5",
      "es6",
      "dom",
      "es2015.core",
      "es2015.collection",
      "es2015.generator",
      "es2015.iterable",
      "es2015.promise",
      "es2015.proxy",
      "es2015.reflect",
      "es2015.symbol",
      "es2015.symbol.wellknown",
      "esnext.asynciterable"
    ],
    target: "es2015",
    experimentalDecorators: true,
    jsx: "react",
  })
