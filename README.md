# Python-Package-Installer-for-Windows

一个面向 Windows 用户的 Python 可视化包安装工具。

它通过本地 Python Agent 管理 Python 环境、虚拟环境和 `pip` 安装任务。用户可以在图形界面中搜索并选择 Python 包，创建独立虚拟环境，查看安装进度、日志和失败原因，无需手动编写 `pip` 命令或 BAT 脚本。

> 当前版本：`V0.7.5`  
> 平台限制：仅支持 Windows  
> 网络要求：安装 Python 包、镜像测速时需要联网

---

## 功能

- Python 环境检测
  - Python 是否可用
  - Python 版本
  - pip 状态
  - Python 可执行文件路径
  - 系统架构

- Python 包目录
  - 16 个分类
  - 600+ 常用 Python 包
  - 搜索、收藏、安装清单
  - 包分类与基础信息展示

- 安装方式
  - 默认创建独立虚拟环境
  - 使用当前 Python 环境
  - 使用已有虚拟环境
  - 选择 Python 命令：`python`、`py`、`python3`
  - 选择 PyPI 镜像源

- 安装任务
  - 后台执行真实 `pip install`
  - 实时安装日志
  - 当前包、总进度、成功数量、失败数量
  - 单个包失败后继续安装后续包
  - 显示退出码和错误输出

- 导入与导出
  - 导入、导出 `requirements.txt`
  - 导入、导出安装配置 JSON
  - 恢复包清单、镜像、Python 命令和虚拟环境设置

- AI 开发模板
  - AI 基础环境
  - 机器学习环境
  - LLM 开发环境
  - 数据分析环境

- 镜像测速
  - 清华镜像
  - 阿里云镜像
  - 中科大镜像
  - 华为云镜像
  - 官方 PyPI
  - 自动推荐响应最快的可用镜像

- UI
  - 中文 / English 切换
  - 深色模式
  - Windows 风格界面
  - 桌面端包列表每行 3 个卡片

---

## 项目结构

```text
Python-Package-Installer-for-Windows/
├── agent/
│   ├── __init__.py
│   ├── catalog_migration.py
│   ├── environment.py
│   ├── installer.py
│   ├── mirror_manager.py
│   ├── pip_manager.py
│   ├── task_manager.py
│   └── venv_manager.py
│
├── frontend/
│   ├── css/
│   ├── js/
│   ├── index.html
│   └── packages.json
│
├── workspace/
├── run_agent.py
└── README.md
```

说明：

- `frontend/`：浏览器界面、样式、JavaScript 和包目录数据。
- `agent/`：本地 Python Agent，负责环境检测、虚拟环境、pip 安装、安装日志和镜像测速。
- `workspace/`：默认工作区。默认虚拟环境会创建在这里。
- `frontend/packages.json`：Python 包分类数据文件。
- `run_agent.py`：启动本地服务的入口。

---

## 运行要求

使用前请确认：

1. 操作系统为 Windows 10 或 Windows 11。
2. 已安装 Python。
3. Python 可以在命令行中运行。
4. 安装包时网络可用。
5. 推荐使用 Python `3.10`、`3.11` 或 `3.12`。

检查 Python 是否安装：

```bat
python --version
```

如果上面的命令无效，可尝试：

```bat
py --version
```

如果两个命令都无法运行，请先安装 Python：

```text
https://www.python.org/downloads/windows/
```

安装 Python 时，务必勾选：

```text
Add Python to PATH
```

---

## 启动方法

### 1. 打开命令提示符

按下：

```text
Win + R
```

输入：

```text
cmd
```

然后按回车。

### 2. 进入项目目录

假设项目位于桌面：

```bat
cd /d "C:\Users\ASUS\Desktop\新建文件夹 (2)"
```

请根据实际项目位置修改目录。

### 3. 启动本地 Agent

运行：

```bat
python run_agent.py
```

如果你的系统使用 Python Launcher，也可以运行：

```bat
py run_agent.py
```

正常启动后，命令行会显示类似内容：

```text
Package catalogue verified: 619 packages in 16 categories.
Python-Package-Installer-for-Windows Agent V0.7.5 listening on http://127.0.0.1:8765
```

### 4. 在浏览器打开页面

打开浏览器，访问：

```text
http://127.0.0.1:8765/
```

不要直接双击 `frontend/index.html`。

原因是项目需要通过本地 Agent 读取 `packages.json`、调用环境检测接口、创建虚拟环境和执行安装任务。直接双击 HTML 文件会使用 `file://` 协议，部分浏览器会阻止读取本地 JSON 或访问接口。

### 5. 停止服务

在运行 Agent 的命令行窗口中按：

```text
Ctrl + C
```

即可停止本地服务。

---

## 基本使用流程

### 安装 Python 包

1. 启动 Agent。
2. 在浏览器打开 `http://127.0.0.1:8765/`。
3. 确认页面显示 Python 环境检测结果。
4. 从分类中选择包，或使用搜索框搜索。
5. 点击“加入清单”。
6. 在右侧安装清单中确认包列表。
7. 选择安装环境。
8. 选择镜像源，或先运行镜像测速。
9. 点击“开始安装”。
10. 在安装页面查看实时日志、成功数和失败数。

建议首次测试时安装较小的包，例如：

```text
colorama
rich
requests
```

不建议首次安装时直接选择大型包，例如：

```text
torch
tensorflow
paddlepaddle
```

这些包下载体积较大，并且可能依赖特定 Python 版本、CPU/GPU、CUDA 版本或系统组件。

---

## 虚拟环境说明

默认推荐选择：

```text
创建新的独立虚拟环境
```

工具会在工作区创建：

```text
workspace/<工作区名称>/.venv/
```

例如工作区名称为 `default`：

```text
workspace/default/.venv/
```

安装命令实际使用的是虚拟环境中的 Python：

```text
workspace/default/.venv/Scripts/python.exe -m pip install <package>
```

这样安装的包不会污染系统全局 Python 环境。

### 环境模式

| 模式 | 说明 | 建议 |
|---|---|---|
| 创建新的独立虚拟环境 | 创建或复用工作区中的 `.venv` | 推荐 |
| 使用当前 Python | 直接安装到当前检测到的 Python 环境 | 仅熟悉 Python 环境时使用 |
| 使用已有虚拟环境 | 使用已存在的虚拟环境 | 适合已有项目 |

---

## requirements.txt

### 导出 requirements.txt

在安装清单中选择好包后，点击导出 `requirements.txt`。

导出内容示例：

```text
numpy
pandas
scikit-learn
```

该文件可以用于其他 Python 项目：

```bat
python -m pip install -r requirements.txt
```

### 导入 requirements.txt

支持导入标准依赖文件：

```text
requests==2.32.3
pandas>=2.0
uvicorn[standard]
```

导入时会：

- 忽略空行；
- 忽略以 `#` 开头的注释；
- 自动去重；
- 拒绝不安全格式；
- 限制最多 100 个包。

---

## 安装配置文件

可以导出当前安装配置为：

```text
Python-Package-Installer-for-Windows.json
```

配置文件包含：

- 环境模式；
- 工作区名称；
- Python 命令；
- 镜像源；
- 安装包清单。

示例：

```json
{
  "format": "Python-Package-Installer-for-Windows",
  "version": "0.7.5",
  "windows_only": true,
  "environment": {
    "mode": "new_venv",
    "workspace": "default",
    "python_command": "python",
    "mirror": "https://pypi.tuna.tsinghua.edu.cn/simple"
  },
  "packages": [
    "numpy",
    "pandas",
    "jupyterlab"
  ]
}
```

导入配置后，页面会恢复包清单和安装设置。

注意：配置文件版本必须与当前程序要求的格式一致。

---

## 镜像测速

项目支持以下镜像：

| 镜像 | 地址 |
|---|---|
| 清华 | `https://pypi.tuna.tsinghua.edu.cn/simple` |
| 阿里云 | `https://mirrors.aliyun.com/pypi/simple/` |
| 中科大 | `https://pypi.mirrors.ustc.edu.cn/simple/` |
| 华为云 | `https://mirrors.huaweicloud.com/repository/pypi/simple/` |
| 官方 PyPI | `https://pypi.org/simple` |

点击“测速并推荐”后，Agent 会测试固定镜像的可访问性和响应时间。

测速不会安装包，也不会下载大型文件。测速结果仅用于推荐镜像，最终是否使用推荐镜像由用户决定。

---

## 安全说明

本项目的本地 Agent 不使用 `shell=True`，不会将用户输入直接拼接为 shell 命令。

pip 命令通过参数数组执行，类似：

```python
subprocess.run(
    [
        python_executable,
        "-m",
        "pip",
        "install",
        package_name
    ],
    shell=False
)
```

自定义包输入会进行格式限制。

允许示例：

```text
requests
requests==2.31.0
pandas>=2.0
uvicorn[standard]
```

不允许示例：

```text
requests & whoami
requests; whoami
-r requirements.txt
https://example.com/package.whl
../package
requests numpy
```

项目仅允许在指定工作区中创建虚拟环境，避免意外覆盖系统目录或任意路径。

---

## 注意事项

### 1. 本项目仅支持 Windows

本项目会创建 Windows 虚拟环境目录：

```text
.venv\Scripts\python.exe
```

并依赖 Windows 下的本地 Python 环境。因此不支持 macOS、Linux、Android 或 iOS。

### 2. Python 3.14 可能存在第三方包兼容性问题

如果你使用的是 Python 3.14，部分第三方包可能暂未发布兼容版本，尤其是：

```text
torch
tensorflow
opencv-python
pandas
scipy
ta-lib
```

遇到安装失败时，建议优先使用 Python 3.11 或 Python 3.12。

### 3. 大型 AI 包需要更多磁盘和网络资源

以下包可能体积较大：

```text
torch
tensorflow
paddlepaddle
transformers
vllm
deepspeed
```

安装前请确认：

- 磁盘空间充足；
- 网络稳定；
- Python 版本符合包要求；
- GPU 相关包与 CUDA 环境匹配。

### 4. GPU 安装不一定适合直接使用默认 PyPI 命令

例如 `torch` 的 GPU 版本通常需要根据：

- CUDA 版本；
- 显卡驱动；
- Python 版本；
- PyTorch 官方安装说明；

选择特定安装命令。

如果 `torch` 安装失败，请优先访问官方安装页面：

```text
https://pytorch.org/get-started/locally/
```

### 5. 安装失败不一定是工具问题

常见失败原因：

- Python 版本不兼容；
- 包不支持 Windows；
- pip 版本过旧；
- 网络连接或镜像不可用；
- 包依赖需要 C/C++ 编译环境；
- GPU / CUDA 环境不匹配；
- 包名、版本号不存在。

工具会尽可能保留 pip 输出和错误信息。遇到失败时，请查看安装页面中的错误日志。

### 6. 不建议使用管理员权限运行

通常不需要以管理员身份打开命令提示符。

默认虚拟环境安装在项目的 `workspace/` 下，不会写入系统目录。只有在选择“使用当前 Python”模式时，才可能影响全局 Python 环境。

### 7. 不要关闭命令行窗口

启动 Agent 后，不要关闭运行 `python run_agent.py` 的命令行窗口。

关闭该窗口后：

- 页面无法读取环境状态；
- 无法创建安装任务；
- 无法查看实时日志；
- 无法安装 Python 包。

---

## 常见问题

### 启动时报 `python 不是内部或外部命令`

说明 Python 未安装，或未加入系统 PATH。

处理方式：

1. 安装 Python。
2. 安装时勾选 `Add Python to PATH`。
3. 关闭并重新打开命令提示符。
4. 执行：

```bat
python --version
```

### 页面显示无法连接本地 Agent

确认：

1. 命令行中已运行：

```bat
python run_agent.py
```

2. 浏览器访问的是：

```text
http://127.0.0.1:8765/
```

3. 没有关闭 Agent 所在的命令行窗口。
4. 端口 `8765` 未被其他程序占用。

### 页面没有显示完整包目录

不要直接双击 `frontend/index.html`。

请通过 Agent 地址打开：

```text
http://127.0.0.1:8765/
```

### 镜像测速显示没有可用镜像

可能原因：

- 网络不可用；
- 公司网络、防火墙或代理限制；
- DNS 异常；
- 镜像站临时不可用。

可切换到官方 PyPI 后重试：

```text
https://pypi.org/simple
```

### 虚拟环境创建失败

检查：

- 当前目录是否有写入权限；
- 磁盘空间是否充足；
- Python 是否支持 `venv`；
- 工作区名称是否包含非法字符。

可在命令行中测试：

```bat
python -m venv test-venv
```

### pip 安装失败

建议按顺序检查：

```bat
python --version
python -m pip --version
python -m pip install --upgrade pip
```

然后尝试使用官方源：

```bat
python -m pip install <package-name> -i https://pypi.org/simple
```
## 开发说明

本项目的设计目标是将 Python 包安装过程拆分为明确职责：

```text
Frontend
    ↓ HTTP / SSE
Local Python Agent
    ↓
Environment Detection
    ↓
Virtual Environment Management
    ↓
pip Installation
    ↓
Task Status and Logs
```
