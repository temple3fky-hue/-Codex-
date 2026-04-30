# Python 图片爬虫下载器（Playwright + Flet）

> 现代化跨平台（桌面/手机）批量下载工具，当前版本优先稳定支持 **Unsplash / Pexels / Pixabay** 图片提取下载。

## 启动一致性检查（已与代码对齐）
- 安装依赖：`pip install -r requirements.txt`
- 安装浏览器：`playwright install chromium`
- 启动程序：`python main.py`
- GUI 按钮：`开始提取并下载 / 暂停 / 恢复 / 停止 / 导出CSV / 导出Excel`

## 技术栈
- 浏览器自动化：**Playwright**
- 网络请求：**requests + httpx + aiohttp**
- HTML 解析：**BeautifulSoup4**
- GUI：**Flet**
- 数据存储：**SQLite**
- 并发下载：**asyncio + aiohttp**

## 平台支持策略
### 当前稳定支持
- Unsplash
- Pexels
- Pixabay

### 暂不深度支持（后续扩展）
- YouTube
- Instagram
- Twitter/X
- Tumblr

## API Key / 环境变量说明
当前版本不依赖平台官方 API，因此 **不需要 API Key** 才能运行。  
如果后续你启用 API 模式，可在 `.env` 中配置（预留）：

```bash
PEXELS_API_KEY=your_key
PIXABAY_API_KEY=your_key
HTTP_PROXY=http://127.0.0.1:7890
HTTPS_PROXY=http://127.0.0.1:7890
```

## 安装与运行

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
python main.py
```

## 使用流程（GUI）
1. 打开程序后，切换到“主界面”。
2. 在 URL 输入框粘贴链接（每行一个）。
3. 点击“开始提取并下载”。
4. 在“下载进度”查看进度和状态。
5. 在“实时日志”查看成功/失败信息。
6. 如需导出，点击“导出CSV”或“导出Excel”。

## 错误提示（已实现）
- 链接无效：输入为空或 URL 非 `http/https`
- 平台不支持：YouTube/Instagram/X/Tumblr 提示“暂不深度支持”
- 网络失败：下载阶段捕获 `aiohttp.ClientError`
- 下载失败：失败自动重试（默认最多 3 次）

## 示例文档
- 见 `docs/quick_start_examples.md`（包含 Unsplash/Pexels/Pixabay 示例链接、下载目录和导出路径）。

## 测试命令
> 请确认 ZIP 中包含 `tests/__init__.py` 与 `tests/test_extractor.py`，否则 `python -m unittest` 可能显示 0 tests。

```bash
# 全量单元测试（离线可跑）
python -m unittest

# 编译检查
python -m compileall main.py gui core downloader models utils tests

# 三站点烟雾测试（需外网与 Playwright 环境）
python tests/smoke_sites.py
```


## Termux 推荐 CLI 模式（无 GUI）
如果 Termux 无法正常打开 Flet GUI，可使用命令行模式：

```bash
# 直接传 URL
python cli.py https://unsplash.com/photos/A-NVHPka9Rk --export-csv

# 从文件读取 URL（每行一个）
python cli.py --file urls.txt --download-dir downloads --concurrency 3 --export-excel
```

## Termux（Android）

```bash
pkg update && pkg upgrade -y
pkg install -y python rust clang cmake libjpeg-turbo libpng freetype
pip install --upgrade pip wheel setuptools
pip install -r requirements.txt
playwright install chromium
python main.py
```

## 打包 EXE（Windows）

```bash
pip install pyinstaller
pyinstaller -F -w main.py -n MediaSpiderGUI
```
