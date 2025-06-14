# 本地环境搭建与测试指南

本文档介绍如何在本地克隆仓库、配置 Python 环境并运行测试用例。

## 1. 克隆仓库

首先从 GitHub 获取项目源代码，命令示例：

```bash
git clone https://github.com/<your_name>/usdpython.git
cd usdpython
```

请将 `<your_name>` 替换为具体仓库地址中的用户名。

## 2. 创建 Python 3.10 Conda 环境

项目依赖 Python 3.10，可使用 conda 创建并激活虚拟环境：

```bash
conda create -n usdpython310 python=3.10
conda activate usdpython310
```

## 3. 安装依赖并配置环境

在激活的虚拟环境中安装所需包，并将 `usdzconvert` 目录加入 `PATH`：

```bash
pip install usd-core numpy pytest
export PATH=$PATH:/path/to/usdpython/usdzconvert
```

请将 `/path/to/usdpython` 替换为仓库的实际路径。若需要使用 FBX SDK，可自行设置 `PYTHONPATH` 指向 FBX Python bindings。

## 4. 运行测试

在仓库根目录执行以下命令即可运行所有测试：

```bash
pytest
```

若环境配置正确，所有测试应当通过。

## 5. 运行示例脚本

仓库 `samples/` 目录包含多个示例脚本，可在配置好环境后直接运行，例如：

```bash
python samples/102_mesh.py
```

脚本会在 `samples/assets` 目录生成对应的 `.usd` 和 `.usdz` 文件。

## 6. 使用 `cube.glb` 测试转换

仓库根目录提供 `cube.glb` 模型，可直接用于验证 `usdzconvert` 的两种材质生成方式：

1. **UsdPreviewSurface 材质（默认）**

   ```bash
   python usdzconvert/usdzconvert cube.glb cube_surface.usdz
   ```

2. **MaterialX 材质**

   ```bash
   python usdzconvert/usdzconvert cube.glb cube_mtlx.usdz -useMaterialX
   ```

如需自定义 MaterialX 库路径，可设置 `MATERIALX_LIB_PATHS` 环境变量，所有 `.mtlx` 文件
会在转换时一并复制到输出包内。

---
以上步骤即完成了本地环境搭建与测试流程。
