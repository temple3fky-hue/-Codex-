"""任务编排。"""
from __future__ import annotations

import asyncio

from core.extractor import extract_media
from downloader.downloader import AsyncDownloader
from models.schemas import AppSettings


class TaskManager:
    def __init__(self, settings: AppSettings, log_cb=None, progress_cb=None):
        self.settings = settings
        self.log_cb = log_cb or (lambda msg: None)
        self.progress_cb = progress_cb or (lambda task: None)
        self.downloader = AsyncDownloader(settings, self.log_cb, self.progress_cb)

    async def run(self, urls: list[str]) -> None:
        all_tasks = []
        for url in urls:
            self.log_cb(f"正在解析: {url}")
            tasks = await extract_media(url, self.settings)
            self.log_cb(f"提取 {len(tasks)} 个资源")
            all_tasks.extend(tasks)
            await asyncio.sleep(0.1)
        self.log_cb(f"总任务数: {len(all_tasks)}")
        await self.downloader.download_tasks(all_tasks)

    def pause(self):
        self.downloader.pause_flag = True

    def resume(self):
        self.downloader.pause_flag = False

    def stop(self):
        self.downloader.stop_flag = True
