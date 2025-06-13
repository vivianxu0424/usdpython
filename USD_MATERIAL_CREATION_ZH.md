# glb -> usdz 材质创建详细设计

本文档结合仓库代码，说明在从 glb/glTF 转换为 USDZ 的过程中，如何解析并构建 USD 材质网络。

## 1. 关键代码位置
- `usdzconvert/usdStageWithGlTF.py` 中的 `createMaterials()` 函数负责解析 glTF 材质并生成 `usdUtils.Material` 实例。
- `usdzconvert/usdUtils.py` 定义 `Material` 类及其 `makeUsdMaterial()` 等方法，用于创建 `UsdShade.Material` 和 `UsdPreviewSurface` 网络。

## 2. glTF 材质解析流程
`createMaterials()` 遍历 `self.gltf['materials']`，为每个材质构建 `usdUtils.Material` 对象，并处理 PBR 参数、贴图及扩展。
代码片段如下：
```python
for gltfMaterial in self.gltf['materials'] if 'materials' in self.gltf else []:
    matName = getName(gltfMaterial, 'material_', len(self.usdMaterials))
    material = usdUtils.Material(matName)
    ...
    usdMaterial = material.makeUsdMaterial(self.asset)
    self.usdMaterials.append(usdMaterial)
```
上述逻辑位于文件 `usdStageWithGlTF.py` 的 632-716 行【F:usdzconvert/usdStageWithGlTF.py†L632-L716】。

在该函数内部主要完成以下任务：
1. 根据 `alphaMode` 设置 `opacity` 或 `opacityThreshold`。
2. 读取 `pbrMetallicRoughness` 或 `KHR_materials_pbrSpecularGlossiness`，并通过 `processTexture()` 处理 `baseColorTexture`、`metallicRoughnessTexture` 等纹理。
3. 解析扩展如 `KHR_materials_clearcoat`，填充 `clearcoat`、`clearcoatRoughness`。
4. 处理 `normalTexture`、`occlusionTexture`、`emissiveTexture` 等其它纹理和属性。

`processTexture()` 会根据 uri 或 bufferView 保存贴图文件、设置包裹模式和 UV 变换，并将结果写入 `material.inputs`。

## 3. 构建 USD 材质网络
`usdUtils.Material.makeUsdMaterial()` 在生成的 Stage 上创建 `UsdShade.Material` 与 `UsdPreviewSurface`，并根据收集到的输入连接纹理节点。
核心实现位于 `usdUtils.py` 第 298-307 行以及相关私有方法【F:usdzconvert/usdUtils.py†L298-L454】。
其流程如下：
1. 在 `makeUsdMaterial()` 中先调用 `_createSurfaceShader()` 构建 `UsdPreviewSurface` 节点，并在需要时设置 `opacityThreshold`。
2. 若 `Material` 含有有效输入，则执行 `updateUsdMaterial()`，该方法遍历所有输入并调用 `_addMapToUsdMaterial()` 创建纹理网络。
3. `_addMapToUsdMaterial()` 会按需生成 `UsdPrimvarReader_float2`、`UsdTransform2d` 和 `UsdUVTexture` 等节点，实现贴图文件、UV 变换和包裹模式的接入。
4. `_makeTextureShaderNames()` 用于合并共享纹理文件，避免重复节点。

以下代码展示了 `_makeUsdUVTexture()` 构建贴图节点的部分逻辑（位于 353-453 行）：
```python
uvReader = UsdShade.Shader.Define(usdStage, uvReaderPath)
uvReader.CreateIdAttr('UsdPrimvarReader_float2')
...
if map.transform != None:
    transformShader = UsdShade.Shader.Define(usdStage, transformShaderPath)
    transformShader.CreateIdAttr('UsdTransform2d')
    ...
textureShader = UsdShade.Shader.Define(usdStage, matPath + '/' + map.textureShaderName + '_texture')
textureShader.CreateIdAttr('UsdUVTexture')
```
【F:usdzconvert/usdUtils.py†L353-L453】

通过上述流程，glTF 材质中的纹理与参数被映射到 USD 的 `UsdPreviewSurface` 网络中，并最终与几何体绑定。

## 4. 调用关系总览
1. `usdzconvert` → `usdStageWithGlTF.usdStageWithGlTF`
2. `glTFConverter.makeUsdStage` 调用 `createMaterials()` 解析材质并生成 `UsdShade.Material`
3. `usdUtils.Material.makeUsdMaterial()` 根据 `inputs` 构建 `UsdPreviewSurface` 及纹理网络

以上描述梳理了 glb/glTF 转换为 USDZ 时的材质创建过程，可作为后续维护与定制的参考。
