from pxr import Usd, UsdShade

def check_shader(usdz_path):
    print("Checking shaders in:", usdz_path)
    stage = Usd.Stage.Open(usdz_path)
    for prim in stage.Traverse():
        if prim.GetTypeName() == "Material":
            mat = UsdShade.Material(prim)
            surf_out = mat.GetSurfaceOutput()
            src = UsdShade.ConnectableAPI.GetConnectedSource(surf_out)
            if src:
                shader = UsdShade.Shader(src[0])
                shader_id = shader.GetIdAttr().Get()
                print(prim.GetPath(), ":", shader_id)

check_shader("cube_surface.usdz")   # 应输出 UsdPreviewSurface
check_shader("cube_mtlx.usdz") # 应输出 ND_standard_surface_surfaceshader
