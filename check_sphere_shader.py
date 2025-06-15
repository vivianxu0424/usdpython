from pathlib import Path
import subprocess
from pxr import Usd, UsdShade
from pygltflib import GLTF2


def gltf_material_info(path):
    gltf = GLTF2().load(str(path))
    mat = gltf.materials[0]
    pbr = mat.pbrMetallicRoughness
    base_color = pbr.baseColorFactor or [1.0, 1.0, 1.0, 1.0]
    metallic = pbr.metallicFactor if pbr.metallicFactor is not None else 1.0
    roughness = pbr.roughnessFactor if pbr.roughnessFactor is not None else 1.0
    alpha = mat.alphaCutoff if mat.alphaMode == 'MASK' else 1.0
    return {
        'diffuseColor': base_color[:3],
        'metallic': metallic,
        'roughness': roughness,
        'opacity': alpha,
    }


def convert(src, dst, use_mtlx=False):
    cmd = ['python', 'usdzconvert/usdzconvert', str(src), str(dst)]
    if use_mtlx:
        cmd.append('-useMaterialX')
    subprocess.check_call(cmd)


def usd_shader_inputs(path, shader_id):
    stage = Usd.Stage.Open(str(path))
    for prim in stage.Traverse():
        if prim.GetTypeName() == 'Material':
            mat = UsdShade.Material(prim)
            out = mat.GetSurfaceOutput()
            src = UsdShade.ConnectableAPI.GetConnectedSource(out)
            if not src:
                continue
            shader = UsdShade.Shader(src[0])
            if shader.GetIdAttr().Get() != shader_id:
                continue
            result = {}
            for name in ['diffuseColor', 'metallic', 'roughness', 'opacity', 'normal']:
                inp = shader.GetInput(name)
                if inp and inp.GetAttr().HasAuthoredValue():
                    result[name] = inp.GetAttr().Get()
            return result
    raise RuntimeError('Shader {} not found in {}'.format(shader_id, path))


def check_material(expected, actual):
    for key, exp in expected.items():
        act = actual.get(key)
        if act is None:
            continue
        if isinstance(exp, (list, tuple)):
            assert all(abs(a - b) < 1e-5 for a, b in zip(act, exp)), f'{key} mismatch: {act} vs {exp}'
        else:
            assert abs(act - exp) < 1e-5, f'{key} mismatch: {act} vs {exp}'


def main():
    src = Path('glb_for_testing/sphere.glb')
    expected = gltf_material_info(src)
    print('Expected material info:', expected)

    surface = Path('sphere_surface.usdc')
    mtlx = Path('sphere_mtlx.usdc')

    convert(src, surface)
    convert(src, mtlx, True)

    surface_inputs = usd_shader_inputs(surface, 'UsdPreviewSurface')
    print('Surface shader inputs:', surface_inputs)
    mtlx_inputs = usd_shader_inputs(mtlx, 'ND_standard_surface_surfaceshader')
    print('MaterialX shader inputs:', mtlx_inputs)

    check_material(expected, surface_inputs)
    check_material(expected, mtlx_inputs)
    print('All checks passed.')


if __name__ == '__main__':
    main()
