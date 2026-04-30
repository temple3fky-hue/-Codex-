"""任务编排。"""
from __future__ import annotations

import asyncio

from models.schemas import AppSettings


class TaskManager:
    def __init__(self, settings: AppSettings, log_cb=None, progress_cb=None, downloader=None):
        self.settings = settings
        self.log_cb = log_cb or (lambda msg: None)
        self.progress_cb = progress_cb or (lambda task: None)
        if downloader is None:
            from downloader.downloader import AsyncDownloader

            downloader = AsyncDownloader(settings, self.log_cb, self.progress_cb)
        self.downloader = downloader

    async def run(self, urls: list[str], extractor=None) -> None:
        if extractor is None:
            from core.extractor import extract_media as extractor
            from core.extractor import ExtractorError, UnsupportedPlatformError
        else:
            class ExtractorError(Exception):
                pass

            class UnsupportedPlatformError(ExtractorError):
                pass

        all_tasks = []
        for url in urls:
            self.log_cb(f"正在解析: {url}")
            try:
                tasks = await extractor(url, self.settings)
                self.log_cb(f"提取 {len(tasks)} 个资源")
                all_tasks.extend(tasks)
            except UnsupportedPlatformError as exc:
                self.log_cb(f"平台不支持: {exc}")
            except ExtractorError as exc:
                self.log_cb(f"解析失败: {exc}")
            except Exception as exc:
                self.log_cb(f"未知错误: {url} -> {exc}")
            await asyncio.sleep(0.1)

        if not all_tasks:
            self.log_cb("没有可下载资源，请检查链接是否有效或平台是否支持。")
            return

        self.log_cb(f"总任务数: {len(all_tasks)}")
        await self.downloader.download_tasks(all_tasks)

    def pause(self):
        self.downloader.pause_flag = True

    def resume(self):
        self.downloader.pause_flag = False

    def stop(self):
        self.downloader.stop_flag = True
