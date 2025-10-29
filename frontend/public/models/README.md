# 3D模型目录

将您的3D Tiles数据集放在此目录下。

## 3D Tiles数据集结构

3D Tiles数据集通常包含以下内容：
- 一个主索引文件 `tileset.json`
- 多个几何数据文件（如 `.b3dm`, `.pnts`, `.i3dm` 等）
- 纹理和其他相关资源文件

## 使用说明

1. 将完整的3D Tiles数据集放入此目录
2. 确保主索引文件命名为 `tileset.json`
3. 在数字孪生页面中，模型路径将自动指向 `/models/tileset.json`

## 示例目录结构

```
models/
├── tileset.json          # 主索引文件
├── tile_001.b3dm         # 几何数据文件
├── tile_002.b3dm         
├── textures/             # 纹理目录（如有）
│   ├── texture_1.jpg
│   └── texture_2.png
└── other_resources/      # 其他资源（如有）
```

## 自定义模型路径

如果您有不同的目录结构或文件名：

1. 在数字孪生页面顶部的输入框中输入完整路径
2. 例如：`/models/my_building/tileset.json`

## 注意事项

- 确保3D Tiles数据集格式正确
- 较大的数据集加载可能需要一些时间
- 若模型未显示，请检查浏览器控制台中的错误信息
- 确保所有相关文件都在同一目录下或正确链接