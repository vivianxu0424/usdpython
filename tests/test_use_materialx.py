import importlib.util
import importlib.machinery
import sys
import types
from pathlib import Path

# create stub modules for pxr and usdUtils to allow importing the script
pxr_stub = types.ModuleType('pxr')
sys.modules.setdefault('pxr', pxr_stub)

usdUtils_stub = types.ModuleType('usdUtils')
class WrapMode:
    black = 'black'
    clamp = 'clamp'
    repeat = 'repeat'
    mirror = 'mirror'
    useMetadata = 'useMetadata'

def isWrapModeCorrect(mode):
    return True

class Material:
    def __init__(self, name):
        self.name = name
        self.inputs = {}
    def isEmpty(self):
        return not self.inputs

usdUtils_stub.WrapMode = WrapMode
usdUtils_stub.isWrapModeCorrect = isWrapModeCorrect
usdUtils_stub.Material = Material
usdUtils_stub.Map = object
usdUtils_stub.Input = types.SimpleNamespace(names=[], channels=[])
usdUtils_stub.printError = lambda *a, **k: None
usdUtils_stub.printWarning = lambda *a, **k: None
usdUtils_stub.ConvertError = Exception
usdUtils_stub.ConvertExit = Exception
sys.modules['usdUtils'] = usdUtils_stub

# load the usdzconvert script as module
script_path = Path(__file__).resolve().parents[1] / 'usdzconvert' / 'usdzconvert'
loader = importlib.machinery.SourceFileLoader('usdzconvert_script', str(script_path))
spec = importlib.util.spec_from_loader(loader.name, loader)
usdz_module = importlib.util.module_from_spec(spec)
loader.exec_module(usdz_module)


def test_use_materialx_flag():
    parser = usdz_module.Parser()
    result = parser.parse(['-useMaterialX', 'cube.glb'])
    assert result.useMaterialX is True
    assert result.inFilePath == 'cube.glb'


def test_default_materialx_flag():
    parser = usdz_module.Parser()
    result = parser.parse(['cube.glb'])
    assert result.useMaterialX is False
