# glb -> usdz 贴图材质处理详细设计

本文件基于仓库现有实现，总结 glb/usdz 转换过程中贴图与材质的解析、构建及连接流程，供后续维护与开发参考。

## 1. 整体流程概览
- `usdzconvert` 脚本检测到输入为 `.gltf` 或 `.glb` 时，调用 `usdStageWithGlTF.usdStageWithGlTF`
- 该函数创建 `glTFConverter` 对象并执行 `converter.makeUsdStage()` 构建 USD Stage
- `makeUsdStage()` 在内部调用 `createMaterials()` 解析 glTF 材质并生成 USD 材质网络

## 2. 读取 glb 数据
`glTFConverter.load()` 根据文件扩展名区分 glb 与 gltf，针对 glb 从二进制块解码 JSON 与缓冲区：
```python
(magic, version, length) = loadChunk(file, '<3i')
(jsonLen, jsonType) = loadChunk(file, '<2i')
self.gltf = json.loads(file.read(jsonLen))
(bufferLen, bufferType) = loadChunk(file, '<2i')
self.buffers.append(file.read())
```
完成解析后，`readAllBuffers()` 负责读取外部或嵌入式 buffer 数据。

## 3. 提取贴图信息
`processTexture()` 处理 glTF 材质中各类纹理描述，支持嵌入式 Base64 与外部文件：
```python
def processTexture(self, dict, type, inputName, channels, material, scaleFactor=None):
    if type not in dict:
        return False
    gltfMaterialMap = dict[type]
    textureIdx = gltfMaterialMap['index']
    gltfTexture = self.gltf['textures'][textureIdx]
    sourceIdx = gltfTexture['source']
    image = self.gltf['images'][sourceIdx]
    # 处理 uri 或 bufferView
    # 根据 sampler 决定 wrapS/wrapT
    # 解析 KHR_texture_transform
    material.inputs[inputName] = usdUtils.Map(
        channels, textureFilename, None, primvarName,
        wrapS, wrapT, scaleFactor, mapTransform)
    return True
```
关键要点包括：
- `saveTexture()`/`saveTextureWithImage()` 将嵌入或引用的贴图数据保存到 `textures/` 目录
- 解析 `samplers` 中的包裹模式设置 `wrapS`、`wrapT`
- 若存在 `KHR_texture_transform`，调用 `convertUVTransformForUSD` 转换为 USD 的 UV 变换参数

## 4. 创建 USD 材质
`createMaterials()` 遍历 `self.gltf['materials']`，对每个材质生成 `usdUtils.Material`：
```python
for gltfMaterial in self.gltf['materials']:
    material = usdUtils.Material(matName)
    pbr = gltfMaterial.get('pbrMetallicRoughness', {})
    self.processTexture(pbr, 'baseColorTexture', usdUtils.InputName.diffuseColor, 'rgb', material, baseColorScale)
    ...
    self.processTexture(gltfMaterial, 'normalTexture', usdUtils.InputName.normal, 'rgb', material)
    self.processTexture(gltfMaterial, 'occlusionTexture', usdUtils.InputName.occlusion, 'r', material)
    if not self.processTexture(gltfMaterial, 'emissiveTexture', usdUtils.InputName.emissiveColor, 'rgb', material, emissiveFactor):
        if 'emissiveFactor' in gltfMaterial:
            material.inputs[usdUtils.InputName.emissiveColor] = emissiveFactor
    usdMaterial = material.makeUsdMaterial(self.asset)
    self.usdMaterials.append(usdMaterial)
```
每个 `usdUtils.Material` 保存了贴图 `Map` 信息和标量/向量输入值。

## 5. 材质与贴图连接
`usdUtils.Material.makeUsdMaterial()` 负责创建 `UsdShade.Material` 及 `UsdPreviewSurface`，随后通过 `updateUsdMaterial()` 根据 `inputs` 构建纹理节点并连接：
- `_makeTextureShaderNames()` 用于合并共享纹理
- `_addMapToUsdMaterial()` 在需要时创建 `UsdPrimvarReader_float2`、`UsdTransform2d` 与 `UsdUVTexture`
- `_makeUsdUVTexture()` 设置贴图文件、UV 变换、包裹模式等属性
这样最终 glTF 中的贴图便与 USD 材质网络中的各端口正确相连。

## 6. 调用关系总览
1. `usdzconvert` → `usdStageWithGlTF.usdStageWithGlTF`
2. `glTFConverter.makeUsdStage`
   - 创建目标 Stage
   - `createMaterials()` → `processTexture()`
   - `material.makeUsdMaterial()` → `updateUsdMaterial()` → `_addMapToUsdMaterial()` → `_makeUsdUVTexture()`

以上过程完成从 glb 贴图读取到 USD 材质节点连接的完整链路，可供开发和调试时查阅。
