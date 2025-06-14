import importlib.util
import importlib.machinery
import sys
import types
from pathlib import Path
import os

# stub modules for pxr and usdUtils
pxr_stub = types.ModuleType('pxr')
sys.modules.setdefault('pxr', pxr_stub)

usdUtils_stub = types.ModuleType('usdUtils')

def copy(src, dst, verbose=False):
    Path(dst).write_bytes(Path(src).read_bytes())

usdUtils_stub.copy = copy
usdUtils_stub.Material = lambda name: types.SimpleNamespace(inputs={}, isEmpty=lambda:True)
usdUtils_stub.Input = types.SimpleNamespace(names=[], channels=[])
usdUtils_stub.WrapMode = types.SimpleNamespace(useMetadata='useMetadata')
usdUtils_stub.NodeManager = lambda: None
usdUtils_stub.printError = lambda *a, **k: None
usdUtils_stub.printWarning = lambda *a, **k: None
sys.modules['usdUtils'] = usdUtils_stub

# load usdzconvert module
script_path = Path(__file__).resolve().parents[1] / 'usdzconvert' / 'usdzconvert'
loader = importlib.machinery.SourceFileLoader('usdzconvert_script', str(script_path))
spec = importlib.util.spec_from_loader(loader.name, loader)
usdz_module = importlib.util.module_from_spec(spec)
loader.exec_module(usdz_module)

def test_copy_materialx_files(tmp_path, monkeypatch):
    cube = Path(__file__).resolve().parents[1] / 'cube.glb'
    parser = usdz_module.Parser()
    result = parser.parse([str(cube)])
    assert result.inFilePath.endswith('cube.glb')

    lib_dir = tmp_path / 'lib'
    lib_dir.mkdir()
    mtlx = lib_dir / 'test.mtlx'
    mtlx.write_text('x')

    dest = tmp_path / 'dest'
    dest.mkdir()

    monkeypatch.setenv('MATERIALX_LIB_PATHS', str(lib_dir))

    usdz_module.copyMaterialXLibraries(str(dest), False)
    assert (dest / 'test.mtlx').exists()
