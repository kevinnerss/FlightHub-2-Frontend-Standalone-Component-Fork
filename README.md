# 司空 2 前端独立组件 
# FlightHub 2 Frontend Standalone Component 
前端组件概述
#基础介绍
#前端组件简介
司空 2 前端组件包括：航线创建，航线编辑器，驾驶舱和项目/地图；同时支持组件的自定义主题色和自定义样式等能力，本手册将介绍如何从零开始将这些组件接入到自有系统。

#开始前的准备
技术栈： React，Vue和原生 HTML + CSS 都可接入。
硬件环境：请参考《大疆司空 2 私有版部署手册》部署司空 2 私有版。
#快速入门
当前版本的司空 2 前端组件主要开放了如下组件及对应功能集合。你可以下载 Demo，参考本手册进行配置和调试。
## 官方指导手册
 - [中文版](https://fh.dji.com/user-manual/cn/custom-development/frontend-components/component-introduction.html)

###  组件

各组件和 demo 的关系如下：

- 驾驶舱：`cockpit.html`
- 航线编辑器：`wayline.html`
- 新建航线弹窗：`wayline-creaction.html`
- 项目地图：`project.html`
- 四分屏示例： `index.html`

其中 `custom-style.css` 为示例的自定义样式


## Official Guidebook
 - [English version](https://fh.dji.com/user-manual/en/custom-development/frontend-components/component-introduction.html)

### Component

The relationship between each component and demo is as follows:

- Cockpit: `cockpit.html`
- Route Editor: `wayline.html`
- New route pop-up window: `wayline-creaction.html`
- Project map: `project.html`
- Quad screen example: `index.html`

`custom-style.css` is the custom style of the example
开发教程
#引入所需的样式和依赖
完成司空 2 私有版部署后，你将获得一个私有 IP，请将该私有 IP （或域名）及端口填入到HEAD代码块的如下位置。

<!DOCTYPE html>
<html>
  <head>
    <script type="text/javascript" src="http://请在此写入私有 IP （或域名）/paas.js" fh2></script>
    <title>Demo</title>
  </head>
  <body>
  </body>
</html>
#前端组件认证信息
司空 2 前端组件开放将依赖司空 2 私有版的能力，因此需要获取司空 2 私有版的认证信息 projectToken 和 项目ID prjId ，获取方式如下：

projectToken: 访问司空 2 私有版，打开【我的组织】页面（部署的司空 2 域名/user-center#/my-organization），在组织列表中点击组织设置，然后点击云端互联面板，可以查看到【组织密钥】，这个组织密钥值就是 projectToken。

prjId：访问司空 2 私有版，点击项目列表，选择某个项目，在链接中查看项目ID，样例如下： https://部署的司空 2 域名/organization/4bf0039f-6434-44a8-b891-8d7b6b7ff132/project/aa9c7a78-4e97-4ced-8953-2cea96c07c00，其中的4bf0039f-6434-44a8-b891-8d7b6b7ff132 为 orgId，aa9c7a78-4e97-4ced-8953-2cea96c07c00 即为 prjId。

#
以航线编辑器为例：

window.FH2.initConfig({
    serverUrl: 'http://请在此写入域名及私有化后端服务端口，默认端口号为30812',
    wssUrl: 'ws://请在此写入域名及私有化后端服务端口，默认端口号为30812/duplex/web',
    hostUrl: 'http://请在此写入私有化web页面ip或域名，以及端口号',
 
    // 复制 prjId 到这里
    prjId: 'cdca2736-8096-4729-9bc7-497ad5b60d5e',
    // 复制 projectToken 到这里
    projectToken: 'MTczMDg4NDI1NHx1NUR3RWxNajc5VnF4QWJuY1BvZmxUenlwYzdnRnBUazFSQnRhMXZOODlPSlVrdFhQekdFTjJKb0I1UkNNUlhtaFR0M3k2WllBdWNJTFVGNDZ4eHp3aWJnSnZ0TjVhNDdNMDUtcUlNQmZRUEtKYjNHeWIyLVZNTm80Qzd6TnMyTUNNSmFsWjZVQ0tkVWtEOU1tWVB5cDNSeWhLQW1NUXJrSzhnQkJhVl9saW5Bazhwbl9KQzg2b2FmWUVULWJoMWowbWh2aEV5X1BtZW9pZm1sRGJmajNoa1QxN280emluNDk1eUFaTUw4ZEJMRmljczIxY0twVmZBNVhiMU81b3Y2UmlNY3dZazFHLTY4Q3ljdFJVdWZuUmVxUUo1VGxEcnJrYkFZNGlpTGVjdC1jNnprYU5nSkFpLWdRbXJ5M2JraEVGUlJJY3YwUUk1TUlDMzZDd2tRc2dlOHNIblFVaHNwb1ozVFJ2MmtoenhZa1pMN0RCbVk4QkVNOVNvaVN1NmszVGRBTE1MMWVLRE5wMFY5VmFrN0FJSzgtcjZaaUstaThwNU9yd0E0V05iNE15eWswc1lXRnFVUzJGZm1wdG0xR0k5WXB0TzRZZUpMeHhCNGVBNEZKZkdaTC1NUV9iRGtXR3EwNXBpOUlBSUd2WFBnYl8tbEJ0NV9qRTRtZG45SDJBZkdpUFZJSktrOFhhSkdqNHEtOUxaUXdvT2NSV0FhUklnQXdINFdFRHR3TGhrPXwr7HTdhghvb4TN9rYRlDyCE9Mzc4Q89m4H3_B24WRKVg=='
})
注意

请确保调用 window.FH2 的方法，是在 页面 load 准备好了之后执行，如你可以使用 addEventListener('load', cb)，在 cb 中调用 window.FH2 的方法。

#添加组件所在的容器
下面以航线编辑器为例，在需要添加航线编辑器的代码区间内插入如下代码：

<div class="fh2-container">
    <div id="wayline-header"></div>
    <div class="project-details">
        <div id="project-app-container"></div>
        <div id="project-middle-container"></div>
        <div id="project-right-micro-app" class="right-micro-app">
            <div class="maps-micro-app">
                <div id="project-map-app-placeholder" class="map-app-placeholder">
                    <div id="map-app-global" class="map-app-container"></div>
                </div>
            </div>
            <div id="wayline-app-container"></div>
        </div>
    </div>
</div>
#添加组件容器样式
下面为推荐的容器样式，可直接在目标代码区域中直接使用，如有其他自定义需求，可自行修改样式代码。

<!DOCTYPE html>
<html>
  <head>
    <!-- start -->
    <style>
        .fh2-container {
            display: flex;
            flex-direction: column;
            /* 设置成你想要加载组件所在容器的宽高 */
            height: 100vh;
            width: 100vw;
        }
 
        #project-app-container>div, .map-app-container>div {
            width: 100%;
            height: 100%;
        }
 
        .project-details {
            position: relative;
            width: 100%;
            display: flex;
            flex: 1;
            overflow: auto;
        }
 
        .project-details .right-micro-app {
            position: relative;
            display: flex;
            flex: 1;
        }
 
        .project-details .right-micro-app .maps-micro-app {
            display: flex;
            flex: 1;
        }
 
        .project-details .right-micro-app .map-app-placeholder {
            flex: 1;
            position: relative;
            display: flex;
            flex-direction: column;
        }
 
        .project-details .right-micro-app .map-app-container {
            height: 100%;
        }
 
        .project-details .right-micro-app #wayline-app-container {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
        }
    </style>
    <title>Demo</title>
  </head>
  <body>
  </body>
</html>
#加载前端组件
下面以航线编辑器为例，传入容器 id 及对应的 wayline_id 后即可加载该组件； 更多的接口说明可查看手册附录的接口文档部分；

window.FH2.loadWayline("wayline-app-container", {
      wayline_id: 'bded3cf1-c924-4cd0-95d0-4bd642ddda09',
})
#自定义地图元素（按需）
下面以地图自定义文本为例，你可以在 Demo 项目中查看自定义文本的效果，点击 wayline.html 页面顶部的地图定制按钮后缩小地图，即可查看效果。

<!DOCTYPE html>
<html>
  <head>
    <link href="./custom-style.css" rel="stylesheet">
  </head>
  <body>
    <div class="btn-bar">
        <button id="CesiumMapBtn" onclick="addCustomCesiumData()">地图定制</button>
    </div>
    <script>
        const CesiumMapBtn = document.getElementById('CesiumMapBtn')
        CesiumMapBtn.style.display = 'none'
        window.addEventListener('load', function () {
            // 等地图实例准备好了，再展示地图定制按钮
            window.FH2.subscribe('cesium-viewer-change', (key) => {
                if (window.FH2.cesiumViewer.global) {
                    CesiumMapBtn.style.display = 'inline-block'
                }
            })
        })
        
        // 示例：定制地图，给地图添加自定义文本
        function addCustomCesiumData () {
            for (const key in window.FH2.cesiumViewer) {
                if (Object.prototype.hasOwnProperty.call(window.FH2.cesiumViewer, key)) {
                    const ins = window.FH2.cesiumViewer[key].entities.add({
                        position: window.Cesium.Cartesian3.fromDegrees(113.93,  22.57, 50),
                        label: {
                            text: "用户自定义文本",
                        },
                    })
                }
            }
        }
    </script>
  </body>
</html>
#自定义主题（按需）
在 Demo 项目中，我们展示了样式自定义的能力，你可以通过修改custom-style.css，更改对应的主题样式，并在 wayline.html 等四个 HTML 文件中直接看到效果 司空 2 组件开发中的的 custom-style.css 使用 CSS 编写，如果你的项目也使用了 CSS，那么可以直接在项目中改变 custom-style 的样式变量。

<!DOCTYPE html>
<html>
  <head>
    <link href="./custom-style.css" rel="stylesheet">
  </head>
  <body>
    <div class="btn-bar">
        <button onclick="changeTheme()">样式定制</button>
    </div>
    <script>
        function changeTheme () {
            document.body.className = document.body.className ? '' : 'set-change-color'
        }
    </script>
  </body>
</html>
3.9 监听组件事件（按需） 下面以航线编辑器为例，对保存按钮进行订阅后，完成航线保存及取消保存时将返回对应提示；

window.FH2.subscribe('wayline-cancel', () => {
    console.log('取消保存航线')
})
window.FH2.subscribe('wayline-save', () => {
    console.log('保存航线')
})


对象实例：window.Cesium
原生 Cesium 对象，能通过 window 对象直接访问，用户无需自己引入cesium.js。

#FAQ
为什么调用 FH2 会报 property undefined 的错误
请确保在网页的 load 阶段后使用 window.FH2 的 API。如果你不确定，可以在 window.load 事件监听的回调函数中使用。

加载司空 2 组件后，网页的 body 背景颜色变成白色
目前加载司空 2 组件会加载 body 背景颜色的全局样式，可能会覆盖网站原本样式，此时你需要对网站的背景颜色设置权重较高的样式，例如使用 !important 样式。


使用司空 2 组件会出现某些界面元素定位不准确的问题
例如在使用航线编辑器的时候，新增航点、添加标注、消息提示等功能，会出现展示的元素发生偏移，定位不准的问题。 解决方案： 请确保组件容器及上层容器不存在以下样式属性： 1.transform 或 perspective 不为 none； 2.filter 不为 none; 3.will-change 为 transform 或 perspective 4.contain 为 paint


如何进行TS类型推导
参考如下代码：

export type eventName = 'wayline-save' | 'wayline-cancel' | 'cesium-viewer-change'
export interface IWaylineParams {
  wayline_id: string;
}
 
export interface ICockpitParams {
  gateway_sn: string;
  drone_sn: string;
}
 
export interface IFH2Config {
  userId: string;
  orgId: string;
  prjId: string;
  serverUrl: string;
  wssUrl: string;
  hostUrl: string;
  token?: string;
}
export interface FH2 extends Record<string, any> {
  validateToken: (token: string) => boolean;
  initConfig: (config: IFH2Config) => void;
  subscribe: (eventName: eventName, callback: (...args: any[]) => void) => void;
  unsubscribe: (eventName: eventName) => void;
  destroyWayline: () => void;
  loadWayline: (domId: string, routerName: string, params?: IWaylineParams) => void;
  updateWayline: (routerName: string, params?: IWaylineParams) => void;
}