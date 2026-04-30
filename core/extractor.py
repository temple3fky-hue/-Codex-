"""网页媒体提取器（Playwright + BeautifulSoup）。"""
from __future__ import annotations

import asyncio
import random
from urllib.parse import urljoin, urlparse

from models.schemas import AppSettings, DownloadTask
from utils.file_utils import guess_filename

SUPPORTED_IMAGE_SITES = {"unsplash.com", "pexels.com", "pixabay.com"}
DEFERRED_VIDEO_SITES = {"youtube.com", "youtu.be", "instagram.com", "x.com", "twitter.com", "tumblr.com"}


class ExtractorError(Exception):
    """提取器错误。"""


class UnsupportedPlatformError(ExtractorError):
    """不支持的平台。"""


class InvalidURLError(ExtractorError):
    """无效链接。"""


class DependencyMissingError(ExtractorError):
    """依赖缺失。"""


def _domain(url: str) -> str:
    return urlparse(url).netloc.lower().replace("www.", "")


def identify_platform(url: str) -> str:
    """识别 URL 平台类型：supported/deferred/other/invalid。"""
    try:
        _validate_url(url)
    except InvalidURLError:
        return "invalid"
    domain = _domain(url)
    if any(domain.endswith(site) for site in SUPPORTED_IMAGE_SITES):
        return "supported"
    if any(domain.endswith(site) for site in DEFERRED_VIDEO_SITES):
        return "deferred"
    return "other"


def _validate_url(url: str) -> None:
    p = urlparse(url)
    if p.scheme not in {"http", "https"} or not p.netloc:
        raise InvalidURLError(f"链接无效: {url}")


async def _render_page_with_playwright(url: str, user_agent: str | None) -> str:
    try:
        from playwright.async_api import TimeoutError as PlaywrightTimeoutError
        from playwright.async_api import async_playwright
    except ImportError as exc:
        raise DependencyMissingError(
            "缺少 Playwright 依赖，请执行: pip install -r requirements.txt && playwright install chromium"
        ) from exc

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(user_agent=user_agent)
            page = await context.new_page()
            await page.goto(url, wait_until="domcontentloaded", timeout=45000)
            for _ in range(6):
                await page.mouse.wheel(0, 7000)
                await asyncio.sleep(random.uniform(0.5, 1.0))
            await page.wait_for_timeout(1200)
            html = await page.content()
            await context.close()
            await browser.close()
            return html
    except PlaywrightTimeoutError as exc:
        raise ExtractorError(f"页面加载超时: {url}") from exc


def _extract_images_from_html(source_url: str, html: str) -> list[DownloadTask]:
    try:
        from bs4 import BeautifulSoup
    except ImportError as exc:
        raise DependencyMissingError(
            "缺少 beautifulsoup4 依赖，请执行: pip install -r requirements.txt"
        ) from exc

    soup = BeautifulSoup(html, "html.parser")
    tasks: list[DownloadTask] = []
    for img in soup.select("img"):
        src = (
            img.get("src")
            or img.get("data-src")
            or img.get("data-lazy-src")
            or img.get("srcset", "").split(" ")[0]
        )
        if not src:
            continue
        full = urljoin(source_url, src)
        lower = full.lower()
        if not any(ext in lower for ext in [".jpg", ".jpeg", ".png", ".webp", "images", "photo"]):
            continue
        tasks.append(DownloadTask(source_url, full, "image", guess_filename(full, "image")))

    dedup = {(t.media_url, t.media_type): t for t in tasks}
    return list(dedup.values())


async def extract_media(url: str, settings: AppSettings, html_provider=None) -> list[DownloadTask]:
    _validate_url(url)
    domain = _domain(url)

    if any(domain.endswith(site) for site in DEFERRED_VIDEO_SITES):
        raise UnsupportedPlatformError(
            f"当前版本暂不深度支持 {domain}，请优先使用 Unsplash/Pexels/Pixabay。"
        )

    user_agent = None
    if settings.user_agent_mode == "random":
        try:
            from fake_useragent import UserAgent

            user_agent = UserAgent().random
        except Exception:
            user_agent = "Mozilla/5.0"

    try:
        html = await html_provider(url) if html_provider else await _render_page_with_playwright(url, user_agent)
        final_tasks = _extract_images_from_html(url, html)
    except ExtractorError:
        raise
    except Exception as exc:
        raise ExtractorError(f"页面解析失败: {url} -> {exc}") from exc

    if any(domain.endswith(site) for site in SUPPORTED_IMAGE_SITES) and not final_tasks:
        raise ExtractorError(f"未提取到图片资源: {url}")
    return final_tasks
