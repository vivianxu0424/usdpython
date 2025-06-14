# 项目概要设计文档

---

### 1. 项目简介
本仓库提供一套称为 **USD Python Tools** 的工具集合，主要功能包含 USDZ 转换、校验与示例脚本等。根据 `README.md` 的说明，工具包内容包括：
- `usdzconvert`：用于将多种文件格式转换为 USDZ
- `usdARKitChecker`：用于验证 USDZ 文件
- 预编译的 Pixar USD 库 Python 模块
- 一组示例脚本以及若干辅助工具，如 `fixOpacity`、`usdzcreateassetlib`、`usdzaudioimport`

### 2. 环境配置
推荐使用 conda 创建 Python 3.7 虚拟环境，并通过 pip 安装 `usd-core` 等依赖：

```bash
conda create -n usdpython37 python=3.7
conda activate usdpython37
pip install usd-core numpy
```

随后将仓库中的 `usdzconvert` 目录加入 `PATH`，并验证工具是否可用：

```bash
export PATH=$PATH:/path/to/usdpython/usdzconvert
usdzconvert -h
```
如需使用 FBX SDK，请自行在 `PYTHONPATH` 中加入其 Python 绑定路径。

### 3. 目录结构
- `README.md`：项目文档及使用说明。
- `LICENSE/`：项目许可证。
- `USD.command`：旧版环境配置脚本，可按需使用。
- `samples/`：示例脚本目录，包含多个示例。
- `usdzconvert/`：核心工具目录，包含转换脚本和各种辅助模块。

### 4. 主要模块
1. **usdzconvert**
   - 主脚本位于 `usdzconvert/usdzconvert`，负责解析命令行参数、调用格式转换模块，并可在转换后执行 `usdARKitChecker` 进行校验。
   - 支持 OBJ、glTF、FBX、Alembic、USD 等多种输入格式。
   - 提供 `-iOS12` 兼容开关，依赖 PIL 完成纹理转换。

2. **格式转换模块**
   - `usdStageWithObj.py`、`usdStageWithFbx.py`、`usdStageWithGlTF.py`：分别负责将对应格式解析为 USD Stage，代码量较大，包含模型、材质和动画转换。
   - `usdMaterialWithObjMtl.py`：解析 OBJ 的 MTL 材质文件。
   - `iOS12LegacyModifier.py`：在输出文件中执行兼容性修改。

3. **校验与工具**
   - `usdARKitChecker`：汇总调用 `validateMesh.py` 与 `validateMaterial.py` 等脚本进行 ARKit 兼容性检查。
   - `fixOpacity`：修复通过旧版 `usdz_converter` 生成的模型不透明问题。
   - `usdzcreateassetlib`：将多个 USDZ 文件合成嵌套的资源库。
   - `usdzaudioimport`：在已存在的 USDZ 文件中加入音频并创建 `SpatialAudio` 节点。

4. **示例脚本**
   位于 `samples/`，展示如何使用 USD Python API 创建 USD 资产，例如 `102_mesh.py` 展示如何生成一个立方体模型并保存为 USDZ。

### 5. 使用方式
1. 依照“环境配置”章节创建并激活 conda 环境，安装依赖后确保 `usdzconvert` 在 `PATH` 中。
2. 执行 `usdzconvert -h` 或其他脚本的 `-h` 选项可查看详细用法。
3. 如需示例，可进入 `samples` 目录运行相应脚本，每个脚本会在 `assets` 子目录下生成 `.usd` 和 `.usdz` 文件，并打印生成的 USD 内容。

### 6. 许可证
项目采用 MIT 许可证，允许自由使用、修改、分发及再授权，但不提供任何明示或暗示的担保。

---

本概要文档对仓库中各文件和脚本进行了概括描述，可作为后续开发或使用该工具集的快速参考。
