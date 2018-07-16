var webpack = require("webpack")
var path = require("path")

const HtmlWebPackPlugin = require("html-webpack-plugin");
const htmlWebpackPlugin = new HtmlWebPackPlugin({
  template: "./src/index.dev.html",
  filename: "./index.html"
});

module.exports = {
  entry: "./src/index.js",
  output: {
    path: path.resolve('build'),
    filename: "main.js",
    sourceMapFilename: "main.map",
  },
  devtool: '#source-map',
  devServer: {
    historyApiFallback: true,
  },
  module: {
    rules: [
      {
        test: /\.js$/,
        exclude: /(node_modules)/,
        use: [{
          loader: 'babel-loader',
          options: {
            babelrc: false,
            presets: [
              'env',
              'stage-0',
              'react'              
            ]
          }
        }]
      },
      {
        test: /\.css$/,
        use: ['style-loader', 'css-loader', {
            loader: 'postcss-loader',
            options: {
              plugins: () => [require('autoprefixer')]
            }
        }]
      },
      {
        test: /\.scss/,
        use: ['style-loader','css-loader', {
            loader: 'postcss-loader',
            options: {
              plugins: () => [require('autoprefixer')]
            }}, 'sass-loader']
    }
    ]
  },
  plugins: [htmlWebpackPlugin]
};