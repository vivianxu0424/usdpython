import importlib.util
import importlib.machinery
import sys
import types
from pathlib import Path

# stub modules for pxr, usdUtils and numpy
pxr_stub = types.ModuleType('pxr')
sys.modules.setdefault('pxr', pxr_stub)

usdUtils_stub = types.ModuleType('usdUtils')
class WrapMode:
    clamp = 'clamp'
    mirror = 'mirror'
    repeat = 'repeat'

class NodeManager:
    def __init__(self):
        pass

usdUtils_stub.WrapMode = WrapMode
usdUtils_stub.NodeManager = NodeManager
usdUtils_stub.makeValidIdentifier = lambda s: s
usdUtils_stub.Asset = object
usdUtils_stub.Skinning = lambda *a, **k: None
usdUtils_stub.ShapeBlending = lambda *a, **k: types.SimpleNamespace()
usdUtils_stub.printError = lambda *a, **k: None
usdUtils_stub.printWarning = lambda *a, **k: None
sys.modules['usdUtils'] = usdUtils_stub

numpy_stub = types.ModuleType('numpy')
sys.modules.setdefault('numpy', numpy_stub)

# load usdStageWithGlTF as module
script_path = Path(__file__).resolve().parents[1] / 'usdzconvert' / 'usdStageWithGlTF.py'
loader = importlib.machinery.SourceFileLoader('usdStageWithGlTF_script', str(script_path))
spec = importlib.util.spec_from_loader(loader.name, loader)
usd_stage_module = importlib.util.module_from_spec(spec)
loader.exec_module(usd_stage_module)

class DummyConverter:
    def __init__(self, gltfPath, usdPath, legacyModifier, openParameters, useMaterialX=False):
        self.flag = useMaterialX
    def makeUsdStage(self):
        return self.flag


def test_usdstage_passes_flag(monkeypatch):
    monkeypatch.setattr(usd_stage_module, 'glTFConverter', DummyConverter)
    openParams = types.SimpleNamespace()
    result = usd_stage_module.usdStageWithGlTF('cube.glb', 'out.usd', False, openParams, True)
    assert result is True
