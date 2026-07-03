const common = require('./webpack.common.js')
const { merge } = require('webpack-merge')
const TerserPlugin = require('terser-webpack-plugin')

module.exports = merge(common, {
  devtool: false,
  optimization: {
    minimize: true,
    minimizer: [
      new TerserPlugin({
        // Avoid multiplying Webpack's memory usage on constrained CI runners.
        parallel: false,
        terserOptions: {
          ecma: 5,
        },
      }),
    ],
  },
})
