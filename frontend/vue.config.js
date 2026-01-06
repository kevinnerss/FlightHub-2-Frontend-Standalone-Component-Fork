const path = require('path')
const webpack = require('webpack')
const CopyWebpackPlugin = require('copy-webpack-plugin')

module.exports = {
  configureWebpack: {
    plugins: [
      new webpack.DefinePlugin({
        CESIUM_BASE_URL: JSON.stringify('./cesium')
      }),
      // 这里是你手动加的，用于复制 Cesium 资源，保持不变
      new CopyWebpackPlugin({
        patterns: [
          {
            from: path.join(__dirname, 'node_modules/cesium/Build/Cesium'),
            to: 'cesium'
          }
        ]
      })
    ],
    // ... 其他 module/resolve 配置保持不变 ...
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
  
  // ---【修改重点在这里】---
  chainWebpack: config => {


    // ... 原有的 Cesium 配置继续往下写 ...
    config.resolve.alias
      .set('cesium', path.resolve(__dirname, 'node_modules/cesium'))
    
    // 移除cesium的prefetch
    config.plugins.delete('prefetch')
    
    // ... 原有的 rule 配置保持不变 ...
    // 静态资源处理
    config.module
      .rule('copyCesiumAssets')
      .test(/Assets[/\\]/)
      .include
        .add(path.resolve(__dirname, 'node_modules/cesium'))
        .end()
      .use('file-loader')
        .loader('file-loader')
        .options({ name: 'cesium/Assets/[name][ext]' })
    
    // Workers处理
    config.module
      .rule('cesiumWorkers')
      .test(/Workers[/\\]/)
      .include
        .add(path.resolve(__dirname, 'node_modules/cesium'))
        .end()
      .use('file-loader')
        .loader('file-loader')
        .options({ name: 'cesium/Workers/[name][ext]' })
    
    // ThirdParty处理
    config.module
      .rule('cesiumThirdParty')
      .test(/ThirdParty[/\\]/)
      .include
        .add(path.resolve(__dirname, 'node_modules/cesium'))
        .end()
      .use('file-loader')
        .loader('file-loader')
        .options({ name: 'cesium/ThirdParty/[name][ext]' })
      
    // 处理Widgets的CSS
    config.module
      .rule('cesiumCSS')
      .test(/Widgets[/\\].*\.css/)
      .include
        .add(path.resolve(__dirname, 'node_modules/cesium'))
        .end()
      .use('css-loader')
        .loader('css-loader')
        .end()
  },
  devServer: {
    static: {
      directory: path.join(__dirname, 'public')
    },
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true
      },
      '/openapi': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true
      }
    }
  }
}
