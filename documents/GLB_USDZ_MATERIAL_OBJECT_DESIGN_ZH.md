# glb -> usdz 材质对象与贴图连接设计

本文详细介绍仓库中将 glb 数据转换为 usdz 过程中，`usdUtils.Material` 与纹理 (`Map`) 对象的构建及连接逻辑，帮助理解材质网络生成的具体实现。

## 1. 核心数据结构

### Map 与 MapTransform
`usdzconvert/usdUtils.py` 中定义的 `Map` 用来描述单张纹理在材质中的使用方式，包括 UV 通道、包裹模式、缩放和变换等信息：
```python
class MapTransform:
    def __init__(self, translation, scale, rotation):
        self.translation = translation
        self.scale = scale
        self.rotation = rotation

class Map:
    def __init__(self, channels, file, fallback=None, texCoordSet='st', wrapS=WrapMode.useMetadata, wrapT=WrapMode.useMetadata, scale=None, transform=None):
        self.file = file
        self.channels = channels
        self.fallback = fallback
        self.texCoordSet = texCoordSet
        self.textureShaderName = ''
        self.wrapS = wrapS
        self.wrapT = wrapT
        self.scale = scale
        self.transform = transform
```
【F:usdzconvert/usdUtils.py†L243-L261】

### Material
`Material` 类存储所有输入属性并在 `makeUsdMaterial()` 中生成 `UsdShade.Material`：
```python
class Material:
    def __init__(self, name):
        ...
        self.inputs = {}
        self.opacityThreshold = None

    def makeUsdMaterial(self, asset):
        matPath = self.path if self.path else asset.getMaterialsPath() + '/' + self.name
        usdMaterial = UsdShade.Material.Define(asset.usdStage, matPath)
        surfaceShader = self._createSurfaceShader(usdMaterial, asset.usdStage)
        if self.isEmpty():
            return usdMaterial
        self.updateUsdMaterial(usdMaterial, surfaceShader, asset.usdStage)
        return usdMaterial
```
【F:usdzconvert/usdUtils.py†L265-L307】

`updateUsdMaterial()` 会遍历 `inputs`，在需要时为每个纹理创建 UVReader、Transform2d 与 UVTexture 等节点：
```python
    def updateUsdMaterial(self, usdMaterial, surfaceShader, usdStage):
        self._makeTextureShaderNames()
        for inputIdx in range(len(Input.names)):
            self._addMapToUsdMaterial(inputIdx, usdMaterial, surfaceShader, usdStage)
```
【F:usdzconvert/usdUtils.py†L292-L297】

## 2. 从 glb 解析材质与纹理

`usdStageWithGlTF.py` 的 `createMaterials()` 读取 glTF 材质并填充 `Material.inputs`：
```python
for gltfMaterial in self.gltf['materials'] if 'materials' in self.gltf else []:
    matName = getName(gltfMaterial, 'material_', len(self.usdMaterials))
    material = usdUtils.Material(matName)
    ...
    if self.processTexture(pbr, 'baseColorTexture', usdUtils.InputName.diffuseColor, 'rgb', material, baseColorScale):
        ...
    self.processTexture(gltfMaterial, 'normalTexture', usdUtils.InputName.normal, 'rgb', material)
    self.processTexture(gltfMaterial, 'occlusionTexture', usdUtils.InputName.occlusion, 'r', material)
    usdMaterial = material.makeUsdMaterial(self.asset)
    self.usdMaterials.append(usdMaterial)
```
【F:usdzconvert/usdStageWithGlTF.py†L633-L720】

其中 `processTexture()` 负责解析 glTF 中的纹理引用、处理包裹模式及 `KHR_texture_transform` 扩展，并将结果写入 `Material.inputs`：
```python
def processTexture(self, dict, type, inputName, channels, material, scaleFactor=None):
    ...
    material.inputs[inputName] = usdUtils.Map(channels, textureFilename, None, primvarName, wrapS, wrapT, scaleFactor, mapTransform)
    return True
```
【F:usdzconvert/usdStageWithGlTF.py†L525-L604】

## 3. 生成 USD 材质网络

当 `makeUsdMaterial()` 被调用时，`Material` 会根据 `inputs` 创建具体的节点连接：
```python
textureShader = self._makeUsdUVTexture(matPath, map, inputName, channels, uvInput, usdStage)
surfaceShader.CreateInput(inputName, inputType).ConnectToSource(textureShader.GetOutput(channels))
```
【F:usdzconvert/usdUtils.py†L485-L507】

`_makeUsdUVTexture()` 内部则负责创建 `UsdPrimvarReader_float2`、`UsdTransform2d`（若有 UV 变换）以及 `UsdUVTexture` 节点，并设置文件路径、包裹模式等属性。

## 4. 调用链回顾
1. `usdzconvert` → `usdStageWithGlTF.usdStageWithGlTF`
2. `glTFConverter.makeUsdStage()` → `createMaterials()`
3. `createMaterials()` 调用 `processTexture()` 将纹理信息存入 `Material.inputs`
4. `material.makeUsdMaterial()` → `updateUsdMaterial()` → `_addMapToUsdMaterial()` → `_makeUsdUVTexture()`

通过上述流程，glb 中定义的材质及纹理被准确转换为 USDZ 中的 `UsdShade.Material` 网络，实现模型与贴图的正确绑定。 
