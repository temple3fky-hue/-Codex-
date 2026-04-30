"""异步下载模块。"""
from __future__ import annotations

import asyncio
from pathlib import Path

import aiohttp

from core.database import insert_history
from models.schemas import AppSettings, DownloadTask
from utils.file_utils import ensure_unique, file_hash


class AsyncDownloader:
    def __init__(self, settings: AppSettings, log_cb=None, progress_cb=None):
        self.settings = settings
        self.log_cb = log_cb or (lambda msg: None)
        self.progress_cb = progress_cb or (lambda task: None)
        self.sem = asyncio.Semaphore(settings.concurrency)
        self.stop_flag = False
        self.pause_flag = False

    async def download_tasks(self, tasks: list[DownloadTask]) -> None:
        async with aiohttp.ClientSession() as session:
            jobs = [self._safe_download(session, t) for t in tasks]
            await asyncio.gather(*jobs)

    async def _safe_download(self, session: aiohttp.ClientSession, task: DownloadTask) -> None:
        for attempt in range(self.settings.max_retries + 1):
            if self.stop_flag:
                task.status = "stopped"
                return
            while self.pause_flag:
                await asyncio.sleep(0.3)
            try:
                await self._download_one(session, task)
                return
            except Exception as exc:
                task.retries += 1
                task.status = "failed"
                task.error = str(exc)
                self.log_cb(f"下载失败({attempt + 1}): {task.media_url} -> {exc}")
        await insert_history(_history_payload(task, None))

    async def _download_one(self, session: aiohttp.ClientSession, task: DownloadTask) -> None:
        async with self.sem:
            out_dir = Path(self.settings.download_dir)
            out_dir.mkdir(parents=True, exist_ok=True)
            target = out_dir / task.filename
            if self.settings.auto_rename:
                target = ensure_unique(target)

            headers = {"User-Agent": "Mozilla/5.0"}
            async with session.get(task.media_url, headers=headers, proxy=self.settings.proxy or None) as resp:
                resp.raise_for_status()
                total = int(resp.headers.get("Content-Length", "0"))
                downloaded = 0
                task.status = "downloading"
                with target.open("wb") as f:
                    async for chunk in resp.content.iter_chunked(1024 * 128):
                        if self.stop_flag:
                            task.status = "stopped"
                            return
                        while self.pause_flag:
                            await asyncio.sleep(0.3)
                        f.write(chunk)
                        downloaded += len(chunk)
                        task.progress = downloaded / total if total else 0
                        self.progress_cb(task)

            task.status = "done"
            task.local_path = str(target)
            task.progress = 1.0
            self.progress_cb(task)
            digest = file_hash(target)
            await insert_history(_history_payload(task, digest))
            self.log_cb(f"下载完成: {task.media_url}")


def _history_payload(task: DownloadTask, digest: str | None) -> dict:
    return {
        "source_url": task.source_url,
        "media_url": task.media_url,
        "media_type": task.media_type,
        "filename": task.filename,
        "status": task.status,
        "local_path": task.local_path,
        "file_hash": digest,
    }
