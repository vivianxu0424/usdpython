import importlib.util
import importlib.machinery
import sys
import types
from pathlib import Path

# stub modules for pxr
pxr_stub = types.ModuleType('pxr')
Tf = types.SimpleNamespace(ErrorException=Exception)

class DummyChecker:
    def __init__(self, *a, **k):
        pass
    def CheckCompliance(self, filename):
        raise Tf.ErrorException("Could not find shader resource: shaderDefs.usda")
    def GetErrors(self):
        return []
    def GetFailedChecks(self):
        return []
    _rules = []

pxr_stub.UsdUtils = types.SimpleNamespace(ComplianceChecker=DummyChecker)
pxr_stub.Tf = Tf
sys.modules.setdefault('pxr', pxr_stub)

# load usdARKitChecker script
script_dir = Path(__file__).resolve().parents[1] / 'usdzconvert'
sys.path.append(str(script_dir))
script_path = script_dir / 'usdARKitChecker'
loader = importlib.machinery.SourceFileLoader('usdARKitChecker_script', str(script_path))
spec = importlib.util.spec_from_loader(loader.name, loader)
usd_checker_module = importlib.util.module_from_spec(spec)
loader.exec_module(usd_checker_module)


def test_missing_shaderdefs_warning():
    errors = []
    result = usd_checker_module.runValidators('dummy.usdz', False, errors)
    assert result is True
    assert errors == []
