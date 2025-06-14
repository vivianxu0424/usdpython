# 本地环境搭建与测试指南

本文档介绍如何在本地克隆仓库、配置 Python 环境并运行测试用例。

## 1. 克隆仓库

首先从 GitHub 获取项目源代码，命令示例：

```bash
git clone https://github.com/<your_name>/usdpython.git
cd usdpython
```

请将 `<your_name>` 替换为具体仓库地址中的用户名。

## 2. 安装 Python 3.7

本项目基于 Python 3.7.9。可以从 [Python 官网](https://www.python.org/downloads/release/python-379/) 下载并安装。

安装完成后，可使用以下命令创建并激活虚拟环境：

```bash
python3.7 -m venv venv
source venv/bin/activate
```

## 3. 配置环境变量

在 macOS 环境中，可直接执行仓库根目录下的 `USD.command` 脚本：

```bash
./USD.command
```

脚本会将 `USD` 及 `usdzconvert` 目录加入 `PATH`，同时设置 `PYTHONPATH`，方便后续使用。如果需要使用 FBX SDK，请按脚本内注释补充相应路径。

如需手动设置环境变量，可参考 `README.md` 中的说明：

```bash
export PATH=$PATH:<PATH_TO_USDPYTHON>/USD
export PYTHONPATH=$PYTHONPATH:<PATH_TO_USDPYTHON>/USD/lib/python
```

其中 `<PATH_TO_USDPYTHON>` 为当前仓库的绝对路径。

## 4. 安装测试依赖

测试脚本依赖 `pytest`，可通过 pip 安装：

```bash
pip install pytest
```

## 5. 运行测试

在仓库根目录执行以下命令即可运行所有测试：

```bash
pytest
```

若环境配置正确，所有测试应当通过。

## 6. 运行示例脚本

仓库 `samples/` 目录包含多个示例脚本，可在配置好环境后直接运行，例如：

```bash
python samples/102_mesh.py
```

脚本会在 `samples/assets` 目录生成对应的 `.usd` 和 `.usdz` 文件。

## 7. 使用 `cube.glb` 测试转换

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
