# USD Python Tools

This package installs to /Applications/usdpython and contains
- `usdzconvert`, a Python-based tool to convert from various file formats to usdz
- `usdARKitChecker`, a Python-based tool for usdz validation
- precompiled macOS Python modules for Pixar's USD library
- a set of sample scripts that demonstrate how to write usd files
- the `fixOpacity` tool
- `usdzcreateassetlib`, a standalone tool to generate an asset library from multiple assets
- `usdzaudioimport`, a standalone tool to attach audio files to usdz files

After installation you can relocate the files.
Many important documents can be found in the `documents` folder.

IMPORTANT! These tools require Python 3.10. We recommend creating a conda environment and installing the USD runtime with pip:

```bash
conda create -n usdpython310 python=3.10
conda activate usdpython310
pip install usd-core numpy
```

Add the `usdzconvert` directory from this repository to your `PATH` so the command can be executed directly:

```bash
export PATH=$PATH:/path/to/usdpython/usdzconvert
```

You can verify the setup by running:

```bash
usdzconvert -h
```

For more details, including demos, see the WWDC 2019 session "Working with USD": 
https://developer.apple.com/videos/play/wwdc2019/602/

## usdzconvert (version 0.66)

`usdzconvert` is a Python script that converts obj, gltf, fbx, abc, and usda/usdc/usd assets to usdz.
It also performs asset validation on the generated usdz.
For more information, run

    usdzconvert -h

### MaterialX Support

`usdzconvert` includes an optional `-useMaterialX` switch. When enabled, the
converter will store a flag in the conversion parameters so that later stages
can generate MaterialX based shader graphs. The default behaviour continues to
produce UsdPreviewSurface materials. When generating a `.usdz` with this option,
any `.mtlx` library files found in paths listed by the `MATERIALX_LIB_PATHS`
environment variable are copied into the package.

### iOS 12 Compatibility

To export .usdz files that play back correctly on iOS 12, use `usdzconvert`'s  `-iOS12` compatibility switch. When run with `-iOS12`, `usdzconvert` will use the Python Imaging Library (PIL) module to do texture conversion. 
If your Python environment is missing PIL, you can install it by running:

    pip install pillow

### FBX Support

Note that FBX support in `usdzconvert` requires both Autodesk's FBX SDK and FBX Python bindings to be installed on your system. Ensure the bindings are on `PYTHONPATH`, for example:

    export PYTHONPATH=$PYTHONPATH:"/Applications/Autodesk/FBX Python SDK/2020.2.1/lib/Python37_x64"

## usdARKitChecker

`usdARKitChecker` is a Python script that validates existing usdz files. It is automatically run by `usdzconvert`, but can also be used as a stand-alone tool to validate files from other sources.
For more information, run 

    usdARKitChecker -h

Currently `usdARKitChecker` consists of three parts:
- validation through Pixar's `usdchecker`
- mesh attribute validation
- UsdPreviewSurface material validation

## Python Package

The USD runtime is delivered via the `usd-core` package installed in the steps above. After activating the conda environment and installing the package, you can import `pxr` modules directly:

```bash
python -c "import pxr; print('USD available')"
```

## Samples

The `samples` folder contains a set of simple scripts that focus on different aspects of writing USD data, such as geometry, materials, skinning and animation. 
Each script generates a .usd and a .usdz file in the `assets` sub folder, and also prints the generated .usd file's content.

| Script | Purpose |
| ------ | --- |
| `101_scenegraph.py` | creates a scene graph |
| `102_mesh.py` | creates a cube mesh |
| `103_simpleMaterial.py` | creates a simple PBR material |
| `104_texturedMaterial.py` | creates a cube mesh and assigns it a PBR material with a diffuse texture |
| `105_pbrMaterial.py` | creates a cube mesh and assigns it a more complex PBR material with textures for normal, roughness and diffuse channels |
| `106_meshGroups.py` | creates a cube mesh with two mesh groups and assigns each a separate material |
| `107_transformAnimation.py` |  builds a scene graph of several objects and sets (animated) translate, rotate, and scale transforms |
| `109_skinnedAnimation.py` | creates an animated skinned cube |
| `201_subdivision.py` | creates a subdivided cube with creases |
| `202_references.py` | creates an asset file then a reference file that reference and overwrite the asset file|

## fixOpacity

If you converted your usdz asset with Xcode's usdz_converter, and it has translucent materials that render opaque in iOS 13, use this script to correct the asset's translucent materials:

    fixOpacity model.usdz

## usdzcreateassetlib

usdzcreateassetlib is a script that generates a single-file asset library from multiple usdz assets. The result is a nested usdz file that contains the source usdz assets and references them in a variant set.
This script does not depend on the USD library, which should make it easy to deploy on servers.

## usdzaudioimport

usdzaudioimport is a script to attach sound/audio files into existing a usdz file. With this tool users can create SpatialAudio nodes in usdz file and specify parameters for it. For more information, run:

    usdzaudioimport -h


