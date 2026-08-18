一个python库半自动化安装脚本，将HTML文件下载到本地双击运行它，2. 左边选分类、中间挑库,点"加入清单"3. 右边点"下载安装脚本",会得到一个 .bat 文件，双击 .bat,弹个黑窗口跑完就行

功能：
-内置 16 个分类、400+个常用库
- 支持搜索、收藏、自定义库名
- 一次勾多个库,合并成一个 bat
- 镜像源切换(默认清华)
- 能选 `python` / `py` / `python3` 三种命令
- 顺手做了个"环境检测"脚本,谁卡住先跑这个
- 主题切换、状态本地保存

已知问题：
-Python 必须装好,且勾选了 Add to PATH,不然 bat 跑起来会报 `不是内部或外部命令`
- `torch` `tensorflow`  这种几个 G 的大库别用清单批量装,容易中途断
- Windows Defender 偶尔会拦自动下载的 bat,需要手动放过

A semi-automatic installation script for a python library. Download the HTML file locally and double-click to run it. 2. Select a category on the left, select a library in the middle, and click "Add to List". 3. Click "Download Installation Script" on the right, and you will get a .bat file. Double-click .bat, and a black window will pop up to finish. Functions: -Built-in 16 categories and 400+ commonly used libraries Supports search, collection, and custom library names Hook multiple libraries at once and merge them into one bat Mirror source switching (default is Tsinghua University) Can choose // three commands pythonpypython3 I conveniently made an "environment detection" script. Whoever gets stuck will run this first. Theme switching, status local saving Known issues: - Python must be installed and Add to PATH is checked, otherwise bat will report that it is not an internal or external command when running. Don't use lists to batch install large libraries of several G like torch tensorflow, as they can easily be interrupted midway. Windows Defender occasionally blocks automatically downloaded bat files and needs to be let go manually.
