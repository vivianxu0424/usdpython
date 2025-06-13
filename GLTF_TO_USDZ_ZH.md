# glTF/glb 转 USDZ 概要流程

本文件概述仓库中 glTF 或 glb 模型转换为 USDZ 的主要步骤，供开发或调试流程时参考。

## 1. 入口脚本 `usdzconvert`
- 通过命令行接收输入与输出文件以及转换选项。
- 当输入扩展名为 `.gltf` 或 `.glb` 时，脚本会导入 `usdzconvert/usdStageWithGlTF.py` 中的 `usdStageWithGlTF` 函数执行转换。

## 2. `usdStageWithGlTF.py` 中的处理流程
- 创建 `glTFConverter` 对象并加载 glTF 数据：
  - `.glb` 文件会解析二进制块并解码嵌入的 JSON 与缓冲区。
  - `.gltf` 文件则直接读取 JSON，并按需加载外部缓冲区与纹理。
- 构建 `usdUtils.Asset` 以生成目标 USD Stage，并初始化材质与节点管理器等辅助结构。
- 主要转换步骤包括：
  1. **材质与纹理**：解析 glTF 的 PBR 参数，生成 `UsdShade` 材质，必要时将纹理文件复制或解码到 `textures/` 目录，并处理包裹模式及 `KHR_texture_transform` 扩展。
  2. **网格与节点层级**：递归遍历 `scenes`/`nodes`，为每个 mesh 创建对应的 `UsdGeom` 几何体，应用位移、旋转、缩放或矩阵变换。
  3. **蒙皮与骨骼**：若模型包含 `skins`，则根据关节与绑定矩阵生成 `UsdSkel` 骨架与权重数据，并在网格上绑定。
  4. **BlendShape**：解析 `targets` 数组以生成形态混合(BlendShape) 相关的 `UsdGeom.Mesh` 属性。
  5. **动画**：读取 `animations`，将位移/旋转/缩放等通道转换为 `UsdGeom.XformOp` 动画曲线，同时支持骨骼动画与形态动画。
- 所有数据写入完成后调用 `asset.finalize()` 设置时间码范围等元数据，并返回生成的 `Usd.Stage` 对象。

## 3. 打包与校验
- `usdzconvert` 收到生成的 `.usdc` 临时文件后，使用 `UsdUtils.CreateNewARKitUsdzPackage` 将其打包为 `.usdz`。
- 若目标是 `.usdz`，脚本还会在结束前运行 `usdARKitChecker` 对生成文件进行 ARKit 兼容性校验。
- 转换完成后删除临时目录并输出最终文件路径。

---
本流程描述了代码中 glTF/glb 到 USDZ 的核心转换逻辑，具体细节可查看 `usdzconvert/usdStageWithGlTF.py` 与 `usdzconvert/usdzconvert` 脚本实现。  
