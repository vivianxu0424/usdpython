import importlib.util
import importlib.machinery
import sys
import types
from pathlib import Path

# stub modules for pxr and numpy
pxr_stub = types.ModuleType('pxr')
sys.modules.setdefault('pxr', pxr_stub)

numpy_stub = types.ModuleType('numpy')
sys.modules.setdefault('numpy', numpy_stub)

# stub usdUtils with minimal structures
usdUtils_stub = types.ModuleType('usdUtils')
class InputName:
    normal = 'normal'
    diffuseColor = 'diffuseColor'
    opacity = 'opacity'
    emissiveColor = 'emissiveColor'
    metallic = 'metallic'
    roughness = 'roughness'
    occlusion = 'occlusion'
    clearcoat = 'clearcoat'
    clearcoatRoughness = 'clearcoatRoughness'

class NodeManager:
    def __init__(self):
        pass

class Input:
    names = [InputName.normal, InputName.diffuseColor, InputName.opacity,
             InputName.emissiveColor, InputName.metallic, InputName.roughness,
             InputName.occlusion, InputName.clearcoat, InputName.clearcoatRoughness]
    channels = ['rgb','rgb','a','rgb','r','r','r','r','r']
    types = [object]*9

class Material:
    def __init__(self, name):
        self.name = name
        self.inputs = {}
        self.used = None
    def isEmpty(self):
        return True
    def makeUsdMaterial(self, asset):
        self.used = 'usd'
        return self
    def makeUsdMaterialX(self, asset):
        self.used = 'mtlx'
        return self

usdUtils_stub.Material = Material
usdUtils_stub.InputName = InputName
usdUtils_stub.Input = Input
usdUtils_stub.Map = object
usdUtils_stub.NodeManager = NodeManager
usdUtils_stub.printError = lambda *a, **k: None
usdUtils_stub.printWarning = lambda *a, **k: None
usdUtils_stub.Asset = lambda path: types.SimpleNamespace(usdStage=None, getMaterialsPath=lambda: '/mats')

sys.modules['usdUtils'] = usdUtils_stub

# load usdStageWithGlTF module
script_path = Path(__file__).resolve().parents[1] / 'usdzconvert' / 'usdStageWithGlTF.py'
loader = importlib.machinery.SourceFileLoader('usdStageWithGlTF_script', str(script_path))
spec = importlib.util.spec_from_loader(loader.name, loader)
usd_stage_module = importlib.util.module_from_spec(spec)
loader.exec_module(usd_stage_module)

# reuse original createMaterials
orig_create = usd_stage_module.glTFConverter.createMaterials

class DummyConverter:
    def __init__(self, gltfPath, usdPath, legacyModifier, openParameters, useMaterialX=False):
        self.useMaterialX = useMaterialX
        self.asset = types.SimpleNamespace(usdStage=None, getMaterialsPath=lambda: '/mats')
        self.gltf = {'materials':[{}]}
        self.usdMaterials = []
        self.processTexture = lambda *a, **k: False
        self.textureHasAlpha = lambda *a, **k: False
        self.verbose = False

    createMaterials = orig_create


def _setup_converter(use_mtlx):
    openParams = types.SimpleNamespace(copyTextures=False, verbose=False)
    conv = DummyConverter('cube.glb', 'out.usd', False, openParams, use_mtlx)
    return conv


def test_create_materials_materialx():
    conv = _setup_converter(True)
    conv.createMaterials()
    assert conv.usdMaterials[0].used == 'mtlx'


def test_create_materials_default():
    conv = _setup_converter(False)
    conv.createMaterials()
    assert conv.usdMaterials[0].used == 'usd'
