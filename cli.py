"""Termux/服务器环境下的命令行模式入口。"""
from __future__ import annotations

import argparse
import asyncio

from core.config import load_settings, save_settings
from core.database import init_db
from core.exporter import export_history_csv, export_history_excel
from core.task_manager import TaskManager


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="图片爬虫下载器 CLI 模式")
    parser.add_argument("urls", nargs="*", help="一个或多个 URL")
    parser.add_argument("--file", help="包含 URL 列表的文本文件（每行一个）")
    parser.add_argument("--download-dir", help="下载目录")
    parser.add_argument("--concurrency", type=int, help="并发数")
    parser.add_argument("--proxy", help="代理地址，例如 http://127.0.0.1:7890")
    parser.add_argument("--export-csv", action="store_true", help="任务完成后导出 CSV")
    parser.add_argument("--export-excel", action="store_true", help="任务完成后导出 Excel")
    return parser


def collect_urls(args: argparse.Namespace) -> list[str]:
    urls = [u.strip() for u in args.urls if u.strip()]
    if args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            urls.extend(line.strip() for line in f if line.strip())
    return list(dict.fromkeys(urls))


async def run_cli(args: argparse.Namespace) -> int:
    urls = collect_urls(args)
    if not urls:
        print("[错误] 请通过位置参数或 --file 提供至少一个 URL。")
        return 2

    settings = load_settings()
    if args.download_dir:
        settings.download_dir = args.download_dir
    if args.concurrency:
        settings.concurrency = args.concurrency
    if args.proxy:
        settings.proxy = args.proxy
    save_settings(settings)

    await init_db()

    def log(msg: str):
        print(msg)

    manager = TaskManager(settings, log_cb=log)
    await manager.run(urls)

    if args.export_csv:
        out = await export_history_csv()
        print(f"CSV 已导出: {out}")
    if args.export_excel:
        out = await export_history_excel()
        print(f"Excel 已导出: {out}")
    return 0


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return asyncio.run(run_cli(args))


if __name__ == "__main__":
    raise SystemExit(main())
