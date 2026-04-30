"""网页媒体提取器（Playwright + BeautifulSoup）。"""
from __future__ import annotations

import asyncio
import random
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from playwright.async_api import async_playwright

from models.schemas import AppSettings, DownloadTask
from utils.file_utils import guess_filename


async def extract_media(url: str, settings: AppSettings) -> list[DownloadTask]:
    ua = UserAgent().random if settings.user_agent_mode == "random" else None
    tasks: list[DownloadTask] = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent=ua)
        page = await context.new_page()
        await page.goto(url, wait_until="networkidle", timeout=60000)

        for _ in range(4):
            await page.mouse.wheel(0, 6000)
            await asyncio.sleep(random.uniform(0.8, 1.5))

        html = await page.content()
        soup = BeautifulSoup(html, "html.parser")

        for img in soup.select("img"):
            src = img.get("src") or img.get("data-src") or img.get("srcset", "").split(" ")[0]
            if not src:
                continue
            full = urljoin(url, src)
            tasks.append(
                DownloadTask(url, full, "image", guess_filename(full, "image"))
            )

        for selector in ["video source", "video", "a"]:
            for node in soup.select(selector):
                src = node.get("src") or node.get("href")
                if not src:
                    continue
                full = urljoin(url, src)
                if any(k in full.lower() for k in [".mp4", ".webm", ".m3u8", "youtube", "youtu.be"]):
                    tasks.append(
                        DownloadTask(url, full, "video", guess_filename(full, "video"))
                    )

        await context.close()
        await browser.close()

    dedup = {(t.media_url, t.media_type): t for t in tasks}
    return list(dedup.values())
