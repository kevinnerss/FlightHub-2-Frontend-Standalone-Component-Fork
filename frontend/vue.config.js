const path = require('path')
const webpack = require('webpack')
const CopyWebpackPlugin = require('copy-webpack-plugin')

module.exports = {
  configureWebpack: {
    plugins: [
      new webpack.DefinePlugin({
        CESIUM_BASE_URL: JSON.stringify('./cesium')
      }),
      new CopyWebpackPlugin({
        patterns: [
          {
            from: path.join(__dirname, 'node_modules/cesium/Build/Cesium'),
            to: 'cesium'
          }
        ]
      })
    ],
    module: {
      rules: [
        {
          test: /\.js$/,
          include: path.resolve(__dirname, 'node_modules/cesium/Source'),
          use: {
            loader: 'babel-loader',
            options: {
              presets: ['@babel/preset-env']
            }
          }
        }
      ]
    },
    resolve: {
      alias: {
        '@': path.resolve(__dirname, 'src')
      }
    }
  },
  chainWebpack: config => {
    config.resolve.alias
      .set('cesium', path.resolve(__dirname, 'node_modules/cesium'))
    
    // 移除cesium的prefetch
    config.plugins.delete('prefetch')
    
    // 静态资源处理 - 使用更兼容的方式
    config.module
      .rule('copyCesiumAssets')
      .test(/Assets[\/\\]/)
      .include
        .add(path.resolve(__dirname, 'node_modules/cesium'))
        .end()
      .use('file-loader')
        .loader('file-loader')
        .options({
          name: 'cesium/Assets/[name][ext]'
        })
    
    // Workers处理
    config.module
      .rule('cesiumWorkers')
      .test(/Workers[\/\\]/)
      .include
        .add(path.resolve(__dirname, 'node_modules/cesium'))
        .end()
      .use('file-loader')
        .loader('file-loader')
        .options({
          name: 'cesium/Workers/[name][ext]'
        })
    
    // ThirdParty处理
    config.module
      .rule('cesiumThirdParty')
      .test(/ThirdParty[\/\\]/)
      .include
        .add(path.resolve(__dirname, 'node_modules/cesium'))
        .end()
      .use('file-loader')
        .loader('file-loader')
        .options({
          name: 'cesium/ThirdParty/[name][ext]'
        })
      
    // 处理Widgets的CSS
    config.module
      .rule('cesiumCSS')
      .test(/Widgets[\/\\].*\.css/)
      .include
        .add(path.resolve(__dirname, 'node_modules/cesium'))
        .end()
      .use('css-loader')
        .loader('css-loader')
        .end()
  },
  devServer: {
    // 配置静态资源目录
    static: {
      directory: path.join(__dirname, 'public')
    },
    // 代理配置（如果需要与后端通信）
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000', // 根据实际后端地址调整
        changeOrigin: true
      }
    }
  }
}