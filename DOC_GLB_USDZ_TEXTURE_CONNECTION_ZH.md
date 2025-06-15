# glb -> usdz 贴图连接流程详细设计

本文档针对仓库中 `usdStageWithGlTF.py` 与 `usdUtils.py` 的实现，梳理从 glb 文件解析到生成 USDZ 材质网络的贴图连接细节。

## 1. 基本流程概览
1. `usdzconvert` 检测到输入扩展名为 `.gltf`/`.glb` 后，导入 `usdStageWithGlTF` 模块并执行 `usdStageWithGlTF()`【F:usdzconvert/usdzconvert†L640-L652】。
2. 该函数实例化 `glTFConverter`，随后调用 `makeUsdStage()` 构建 `Usd.Stage`【F:usdzconvert/usdStageWithGlTF.py†L1525-L1530】。
3. `makeUsdStage()` 在内部依次执行 `createMaterials()`、节点和动画处理，最终 `asset.finalize()` 完成 Stage 设置【F:usdzconvert/usdStageWithGlTF.py†L1504-L1523】。

## 2. 解析 glb 并保存贴图
- `glTFConverter.load()` 根据文件扩展名判断是否为 `.glb`，若是则解析二进制区块，解码 JSON 与 Buffer【F:usdzconvert/usdStageWithGlTF.py†L424-L440】。
- `readAllBuffers()` 在解析完成后将外部或嵌入式的 buffer 数据读入到 `self.buffers`【F:usdzconvert/usdStageWithGlTF.py†L607-L621】。
- 在处理纹理时，`processTexture()` 会根据 `image` 信息决定贴图来源：
  - 对于嵌入式 `data:` URI，通过 `base64.b64decode` 解码后调用 `saveTexture()` 写入 `textures/texgen_xx` 文件【F:usdzconvert/usdStageWithGlTF.py†L538-L548】。
  - 若 `image` 提供 `bufferView`，则 `saveTextureWithImage()` 根据视图数据保存到文件【F:usdzconvert/usdStageWithGlTF.py†L513-L522】【F:usdzconvert/usdStageWithGlTF.py†L564-L566】。
  - 普通文件 URI 情况下，会将原始图片复制或重命名到目标目录【F:usdzconvert/usdStageWithGlTF.py†L549-L562】。

## 3. 构建材质输入
`createMaterials()` 遍历 glTF 材质并对每个通道调用 `processTexture()` 或写入常量值【F:usdzconvert/usdStageWithGlTF.py†L633-L720】。其中：
- 根据 `sampler` 设置 `wrapS`、`wrapT` 包裹模式【F:usdzconvert/usdStageWithGlTF.py†L577-L587】。
- 如果检测到 `KHR_texture_transform` 扩展，则通过 `convertUVTransformForUSD()` 生成适配 USD 的变换参数并构造 `usdUtils.MapTransform`【F:usdzconvert/usdStageWithGlTF.py†L591-L602】。
- `processTexture()` 最终向 `usdUtils.Material` 的 `inputs` 字典写入 `usdUtils.Map`，记录贴图文件路径、UV 集名称及变换信息【F:usdzconvert/usdStageWithGlTF.py†L603-L604】。

## 4. 生成 USD 材质网络
- `usdUtils.Material.makeUsdMaterial()` 会创建 `UsdShade.Material` 与 `UsdPreviewSurface` 节点，并调用 `_makeTextureShaderNames()` 合并共享贴图【F:usdzconvert/usdUtils.py†L292-L314】。
- 随后 `updateUsdMaterial()` 根据各 `inputs` 调用 `_addMapToUsdMaterial()`【F:usdzconvert/usdUtils.py†L316-L319】【F:usdzconvert/usdUtils.py†L485-L507】。
- `_addMapToUsdMaterial()` 内部通过 `_makeUsdUVTexture()` 创建 `UsdPrimvarReader_float2`、可选的 `UsdTransform2d` 以及 `UsdUVTexture` 节点，并连接到 `UsdPreviewSurface` 的相应端口【F:usdzconvert/usdUtils.py†L353-L452】【F:usdzconvert/usdUtils.py†L485-L507】。

## 5. 流程总结
综上所述，glb 转换为 USDZ 的贴图连接流程大致如下：
1. 解析 glb 数据，读取 buffer 与图片资源。
2. `processTexture()` 对每个材质通道解析图片来源并保存到目标目录，同时记录包裹模式和 UV 变换。
3. `createMaterials()` 将这些信息填充到 `usdUtils.Material` 对象。
4. `makeUsdMaterial()` 按需生成纹理读取节点和 `UsdPreviewSurface`，确保贴图在 USD 材质网络中正确连接。

通过以上步骤，即可将 glb 中的纹理资源完整地映射到 USDZ 文件内的材质结构中。
