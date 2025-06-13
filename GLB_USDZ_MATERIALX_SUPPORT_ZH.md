# glb -> usdz MaterialX Shader 支持概要设计

当前仓库在将 glb 模型转换为 usdz 时，仅生成基于 **UsdPreviewSurface** 的材质网络，
难以表达更复杂的材质效果。为了在苹果或 Pixar 等生态中更好地利用 MaterialX 标准，
计划在转换流程中新增对 **MaterialX Shader** 的支持。本文档概述该功能的设计思路。

## 1. 目标与原则
- 保持现有 `usdzconvert` 使用方式不变，新增可选开关 `--use-materialx` 启用 MaterialX。
- 在 glTF 材质解析阶段，依据该开关构建对应的 **UsdShade.Material** 网络：
  - 默认仍生成 UsdPreviewSurface，以兼容旧流程。
  - 开启开关后，生成遵循 MaterialX 标准的节点和连接。
- 材质参数映射遵循 glTF PBR 金属度/粗糙度模型，转换为 MaterialX `standard_surface` 等节点输入。
- 代码层面尽量复用 `usdUtils.Material` 的结构，新增 `_createMaterialXShader()` 等私有方法实现具体节点构建。

## 2. 转换流程修改
1. **命令行解析**：在 `usdzconvert/usdzconvert` 中加入 `--use-materialx` 选项，传递给 `usdStageWithGlTF.usdStageWithGlTF`。
2. **材质创建**：`usdStageWithGlTF.createMaterials()` 增加判断，根据开关选择调用 `Material.makeUsdMaterial()` 或新实现 `makeUsdMaterialX()`。
3. **MaterialX 节点生成**：在 `usdUtils.Material` 内实现 `makeUsdMaterialX()`，步骤包括：
   - 创建 `UsdShade.Material` 实例。
   - 调用 `_createMaterialXShader()` 生成 `nd_standard_surface` 节点，并根据贴图或常量输入连接相关端口（如 `base_color`, `metalness`, `roughness`）。
   - 将生成的 `materialXShader` 的 `out` 输出连接到 `surface`。
4. **材质库依赖**：打包 usdz 时将所需的 MaterialX `.mtlx` 库文件一并复制到包内，以便运行时解析。
5. **向后兼容**：若目标查看器不支持 MaterialX，可在命令行关闭该功能，或在生成的 USD 中同时保留 PreviewSurface 供回退使用。

## 3. 后续工作
- 细化 glTF 到 MaterialX 参数映射表，处理法线贴图、透明度等进阶特性。
- 研究 KHR_materials_xxx 等扩展以携带更丰富的材质信息。
- 引入单元测试，确保在两种模式下生成的 USD 都能被查看器正确加载。

以上为在 glb -> usdz 流程中加入 MaterialX Shader 支持的初步设计，具体实现细节可
在后续开发中进一步补充与优化。

