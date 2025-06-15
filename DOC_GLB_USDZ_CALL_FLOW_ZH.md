# glb -> usdz 函数调用关系概述详细设计

本文档结合仓库代码，按调用顺序梳理 glb 模型转换为 usdz 文件时各函数之间的关系，便于进一步理解整体实现。

## 1. 总体流程入口 `usdzconvert`
- 位于 `usdzconvert/usdzconvert` 脚本。
- 解析命令行参数后，依据输入文件扩展名选择相应转换模块。
- 当扩展名为 `.glb` 或 `.gltf` 时，执行：
  ```python
  usdStageWithGlTF_module = importlib.import_module("usdStageWithGlTF")
  usdStage = usdStageWithGlTF_module.usdStageWithGlTF(srcPath, tmpPath, legacyModifier, openParameters)
  ```
- 返回的 `usdStage` 随后被写出并在需要时打包成 `.usdz`，同时执行 `usdARKitChecker` 进行校验。

## 2. 模块 `usdStageWithGlTF`
- 文件路径：`usdzconvert/usdStageWithGlTF.py`。
- 提供顶层函数 `usdStageWithGlTF(gltfPath, usdPath, legacyModifier, openParameters)`，主要工作：
  1. 创建 `glTFConverter` 对象：`converter = glTFConverter(gltfPath, usdPath, legacyModifier, openParameters)`。
  2. 调用 `converter.makeUsdStage()` 完成所有转换并返回 `Usd.Stage`。

## 3. 类 `glTFConverter`
- 负责解析 glb 数据并生成目标 Stage，核心方法包括：
  - `load()`：根据扩展名读取 `.glb` 或 `.gltf` 内容，解析 JSON 和二进制缓冲区。
  - `readAllBuffers()`：按需加载外部 buffer 数据。
  - `createMaterials()`：遍历 glTF 材质，内部多次调用 `processTexture()` 处理贴图，并通过 `usdUtils.Material` 构建 `UsdShade` 网络。
  - `prepareSkinning()`：解析 `skins` 生成 `UsdSkel.Skeleton` 相关数据。
  - `prepareBlendShapes()`：检查 `mesh` 的 `targets`，创建形态混合数据结构。
  - `prepareAnimations()`：统计动画帧率，为后续曲线采样做准备。
  - `processNodeChildren()`/`processNode()`：递归遍历场景节点，创建 `UsdGeom` 实例并设置变换，同时记录网格与骨骼的关联。
  - `processSkeletonAnimation()`、`processBlendShapeAnimations()`、`processNodeTransformAnimation()`：分别处理骨骼动画、形态动画和普通节点动画，调用 `getInterpolatedValues()` 计算关键帧曲线。
  - `processSkinnedMeshes()`、`processBlendShapeMeshes()`：在前期收集信息后实际生成带蒙皮或 BlendShape 的网格。
  - `asset.finalize()`：由 `usdUtils.Asset` 提供，写入 Stage 元数据并设置时间码范围。

### `makeUsdStage()` 调用链
该方法串联了上述步骤，伪代码顺序如下：
```python
self.usdStage = self.asset.makeUsdStage()
self.createMaterials()
self.prepareSkinning()
self.prepareBlendShapes()
self.prepareAnimations()
self.processNodeChildren(self.gltf['scenes'][0]['nodes'], self.asset.getGeomPath(), None)
self.processSkeletonAnimation()
self.processBlendShapeAnimations()
self.processSkinnedMeshes()
self.processBlendShapeMeshes()
self.processNodeTransformAnimation()
self.shapeBlending.flush()
self.asset.finalize()
return self.usdStage
```

## 4. 辅助模块 `usdUtils`
- 位于 `usdzconvert/usdUtils.py`，提供 `Asset`、`Material`、`Skinning`、`ShapeBlending` 等辅助类。
- `glTFConverter` 在材质、骨骼和形态处理过程中均大量依赖这些工具类来创建和管理 USD 实体。

## 5. 完成打包与校验
- `usdzconvert` 在收到临时生成的 `.usdc` 文件后，调用 `UsdUtils.CreateNewARKitUsdzPackage` 打包为 `.usdz`。
- 若目标为 `.usdz`，随后执行 `usdARKitChecker` 脚本对生成文件进行兼容性校验。

---
以上内容概述了从命令行调用到最终生成 usdz 的主要函数关系，便于开发人员快速定位各阶段实现。 
