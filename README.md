# Python 图片/视频爬虫下载器（Playwright + Flet）

> 现代化跨平台（桌面/手机）批量下载工具，支持 URL 列表、动态页面提取、下载队列和历史管理。

## 技术栈确认
- 浏览器自动化：**Playwright**（支持 JS 渲染、懒加载、滚动加载）
- 网络请求：**requests + httpx + aiohttp**
- HTML 解析：**BeautifulSoup4**
- GUI：**Flet**（桌面/移动端友好）
- 数据存储：**SQLite**（下载历史）
- 并发下载：**asyncio + aiohttp**
- 导出：**CSV/Excel**（pandas/openpyxl）

## 功能特性
- 输入单个或多个 URL（每行一个）
- 自动提取网页图片/视频资源链接（含部分动态内容）
- 下载队列、暂停/恢复/停止、失败自动重试（最多3次）
- SQLite 历史记录、CSV/Excel 导出
- 设置中心：代理、并发数、下载目录、自动重命名、跳过已存在文件
- 基础反爬策略：随机 UA、滚动延迟、浏览器自动化加载

## 项目结构

```text
.
├── main.py
├── requirements.txt
├── core/
│   ├── config.py
│   ├── database.py
│   ├── extractor.py
│   ├── exporter.py
│   └── task_manager.py
├── downloader/
│   └── downloader.py
├── gui/
│   └── app.py
├── models/
│   └── schemas.py
├── utils/
│   ├── file_utils.py
│   └── logger.py
├── data/               # 运行后生成（settings、db、日志）
└── exports/            # 导出文件
```

## 安装与运行

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
python main.py
```

## Termux（Android）安装命令

```bash
pkg update && pkg upgrade -y
pkg install -y python rust clang cmake libjpeg-turbo libpng freetype
pip install --upgrade pip wheel setuptools
pip install -r requirements.txt
playwright install chromium
python main.py
```

> 提示：部分 Android 设备上 Playwright 浏览器依赖可能受限，如启动失败请优先在桌面 Linux/Windows 运行。

## 打包 EXE（Windows）

```bash
pip install pyinstaller
pyinstaller -F -w main.py -n MediaSpiderGUI
```

## 常见平台支持说明
- Unsplash / Pexels / Pixabay / 壁纸站：优先解析 HTML + 动态加载后的 DOM
- YouTube：可提取部分视频链接/缩略图；复杂流媒体可能需配合 yt-dlp（可后续扩展）
- Twitter(X) / Instagram / Tumblr：依赖 Playwright 登录态/滚动，受平台策略影响较大
- m3u8：当前版本会识别链接，后续可扩展 ffmpeg 合并下载链路

## 后续增强建议
- 增加网站级插件（每站独立提取器）
- 接入 Cookie 持久化 + 登录态管理
- 增加文件夹自动分类（按站点/日期/媒体类型）
- 增加 AI 标签识别与自动命名

