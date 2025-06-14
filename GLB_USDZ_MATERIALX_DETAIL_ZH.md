# glb -> usdz MaterialX Shader 支持详细设计

本文档进一步说明在现有 glb 转 usdz 流程中加入 MaterialX Shader 的代码改动方案，
涵盖新增函数及需要调整的旧函数。

## 1. 新增命令行参数
- 在 `ParserOut` 结构中增加 `useMaterialX` 字段，供命令行解析结果保存开关状态【F:usdzconvert/usdzconvert†L45-L65】。
- `OpenParameters` 同样新增 `useMaterialX` 成员，便于在转换器阶段读取【F:usdzconvert/usdzconvert†L68-L75】。
- `printUsage()` 输出中加入 `-useMaterialX` 选项说明【F:usdzconvert/usdzconvert†L93-L129】。
- 参数解析逻辑检测 `-useMaterialX`，并设置 `ParserOut.useMaterialX` 的值【F:usdzconvert/usdzconvert†L324-L344】。
- 调用 `usdStageWithGlTF` 时，将该开关写入 `OpenParameters` 并一并传递【F:usdzconvert/usdzconvert†L638-L649】。

## 2. `usdStageWithGlTF` 与 `glTFConverter`
- `usdStageWithGlTF()` 函数新增 `useMaterialX` 参数，并在创建 `glTFConverter` 时传递【F:usdzconvert/usdStageWithGlTF.py†L1525-L1530】。
- 在 `glTFConverter.__init__()` 中保存此标记，例如 `self.useMaterialX = openParameters.useMaterialX`，以便后续流程判断【F:usdzconvert/usdStageWithGlTF.py†L398-L418】。

## 3. MaterialX 材质生成
 - 在 `usdUtils.Material` 内实现 `makeUsdMaterialX()`，整体流程与现有 `makeUsdMaterial()`【F:usdzconvert/usdUtils.py†L298-L307】 类似。
  - 该函数调用新私有方法 `_createMaterialXShader()` 创建 `nd_standard_surface` 节点，并连接 `UsdShade.Material` 的 `surface` 输出。
 - `_addMapToUsdMaterial()` 保持旧实现不变，另新增 `_addMapToMaterialX()` 处理 MaterialX 节点的贴图输入，可参考当前实现【F:usdzconvert/usdUtils.py†L498-L559】。

## 4. 调整材质创建流程
 - `createMaterials()` 在生成 `usdUtils.Material` 后，根据 `self.useMaterialX` 选择调用 `makeUsdMaterialX()` 或 `makeUsdMaterial()`【F:usdzconvert/usdStageWithGlTF.py†L633-L720】。
- 若启用 MaterialX，打包 `.usdz` 时应同时复制所需的 `.mtlx` 库文件，确保运行时可以解析。

通过以上修改，命令行添加 `-useMaterialX` 后即可在转换阶段生成基于 MaterialX 的 `UsdShade.Material` 网络，同时保持旧接口与 UsdPreviewSurface 的兼容。 
