#!/usr/bin/env python3.10

# Creates a cube mesh and assigns it a more complex PBR material with textures for normal, roughness and diffuse channels

from pxr import *

assetName = 'pbrMaterial'
stage = Usd.Stage.CreateNew('assets/' + assetName + '.usd')

UsdGeom.SetStageUpAxis(stage, 'Y')

# create rootPrim, define asset metadata and set as defaultPrim
rootPrim = stage.DefinePrim('/' + assetName, 'Xform')
Usd.ModelAPI(rootPrim).SetKind('component')
rootPrim.SetAssetInfoByKey('name', assetName)
rootPrim.SetAssetInfoByKey('identifier', Sdf.AssetPath(assetName + ".usd")) 
stage.SetDefaultPrim(rootPrim)

# create mesh with texture coordinates
stage.DefinePrim('/' + assetName + '/Geom', 'Scope')
mesh = UsdGeom.Mesh.Define(stage, '/' + assetName + '/Geom/cube')
mesh.CreateSubdivisionSchemeAttr().Set(UsdGeom.Tokens.none)
mesh.CreatePointsAttr([(-0.5, -0.5, 0.5), (0.5, -0.5, 0.5), (-0.5, 0.5, 0.5), (0.5, 0.5, 0.5), (-0.5, 0.5, -0.5), (0.5, 0.5, -0.5), (-0.5, -0.5, -0.5), (0.5, -0.5, -0.5)])
mesh.CreateExtentAttr(UsdGeom.PointBased(mesh).ComputeExtent(mesh.GetPointsAttr().Get()))
mesh.CreateNormalsAttr([(0,0,1), (0,1,0), (0,0,-1), (0,-1,0), (1,0,0), (-1,0,0)])
mesh.SetNormalsInterpolation(UsdGeom.Tokens.uniform)

mesh.CreateFaceVertexCountsAttr([4, 4, 4, 4, 4, 4])
mesh.CreateFaceVertexIndicesAttr([0, 1, 3, 2, 2, 3, 5, 4, 4, 5, 7, 6, 6, 7, 1, 0, 1, 7, 5, 3, 6, 0, 2, 4])

textureCoordinates = mesh.CreatePrimvar('st', Sdf.ValueTypeNames.TexCoord2fArray, UsdGeom.Tokens.faceVarying)
textureCoordinates.Set([(0.375, 0), (0.625, 0), (0.625, 0.25), (0.375, 0.25), (0.625, 0.5), (0.375, 0.5), (0.625, 0.75), (0.375, 0.75), (0.625, 1), (0.375, 1), (0.875, 0), (0.875, 0.25), (0.125, 0), (0.125, 0.25)])
textureCoordinates.SetIndices(Vt.IntArray([0, 1, 2, 3, 3, 2, 4, 5, 5, 4, 6, 7, 7, 6, 8, 9, 1, 10, 11, 2, 12, 0, 3, 13]))

# create PBR material
stage.DefinePrim('/' + assetName + '/Materials', 'Scope')
material = UsdShade.Material.Define(stage, '/' + assetName + '/Materials/cubeMaterial')
texCoordInput = material.CreateInput('frame:stPrimvarName', Sdf.ValueTypeNames.Token)
texCoordInput.Set('st')

pbrShader = UsdShade.Shader.Define(stage, '/' + assetName + '/Materials/cubeMaterial/PBRShader')
pbrShader.CreateIdAttr('UsdPreviewSurface')

# create texture coordinate attribute reader node
texCoordReader = UsdShade.Shader.Define(stage, '/' + assetName + '/Materials/cubeMaterial/texCoordReader')
texCoordReader.CreateIdAttr('UsdPrimvarReader_float2')
texCoordReader.CreateInput('varname',Sdf.ValueTypeNames.Token).ConnectToSource(texCoordInput)
texCoordReader.CreateOutput('result', Sdf.ValueTypeNames.Float2)

# diffuse texture
diffuseTextureSampler = UsdShade.Shader.Define(stage, '/' + assetName + '/Materials/cubeMaterial/diffuseTexture')
diffuseTextureSampler.CreateIdAttr('UsdUVTexture')
diffuseTextureSampler.CreateInput('file', Sdf.ValueTypeNames.Asset).Set('textures/soccerBall_BC.png')
diffuseTextureSampler.CreateInput('st', Sdf.ValueTypeNames.Float2).ConnectToSource(texCoordReader, 'result')
diffuseTextureSampler.CreateOutput('rgb', Sdf.ValueTypeNames.Float3)
pbrShader.CreateInput('diffuseColor', Sdf.ValueTypeNames.Color3f).ConnectToSource(diffuseTextureSampler, 'rgb')

# set metalness = 0
pbrShader.CreateInput('metallic', Sdf.ValueTypeNames.Float).Set(0.0)

# roughness texture
roughnessTextureSampler = UsdShade.Shader.Define(stage, '/' + assetName + '/Materials/cubeMaterial/roughnessTexture')
roughnessTextureSampler.CreateIdAttr('UsdUVTexture')
roughnessTextureSampler.CreateInput('file', Sdf.ValueTypeNames.Asset).Set('textures/soccerBall_R.png')
roughnessTextureSampler.CreateInput('st', Sdf.ValueTypeNames.Float2).ConnectToSource(texCoordReader, 'result')
roughnessTextureSampler.CreateOutput('r', Sdf.ValueTypeNames.Float)
pbrShader.CreateInput('roughness', Sdf.ValueTypeNames.Float).ConnectToSource(roughnessTextureSampler, 'r')

# normal texture
normalTextureSampler = UsdShade.Shader.Define(stage, '/' + assetName + '/Materials/cubeMaterial/normalTexture')
normalTextureSampler.CreateIdAttr('UsdUVTexture')
normalTextureSampler.CreateInput('file', Sdf.ValueTypeNames.Asset).Set('textures/soccerBall_N.png')
normalTextureSampler.CreateInput('st', Sdf.ValueTypeNames.Float2).ConnectToSource(texCoordReader, 'result')
normalTextureSampler.CreateInput('scale', Sdf.ValueTypeNames.Float4).Set((2.0, 2.0, 2.0, 2.0))
normalTextureSampler.CreateInput('bias', Sdf.ValueTypeNames.Float4).Set((-1.0, -1.0, -1.0, -1.0))
normalTextureSampler.CreateOutput('rgb', Sdf.ValueTypeNames.Float3)
pbrShader.CreateInput('normal',Sdf.ValueTypeNames.Normal3f).ConnectToSource(normalTextureSampler, 'rgb')

material.CreateSurfaceOutput().ConnectToSource(pbrShader, 'surface')

# bind material to mesh
UsdShade.MaterialBindingAPI(mesh.GetPrim()).Bind(material)

print(stage.GetRootLayer().ExportToString())
stage.Save()

# construct .usdz archive from the .usdc file
UsdUtils.CreateNewARKitUsdzPackage('assets/'+assetName+'.usd', 'assets/'+assetName+'.usdz')
