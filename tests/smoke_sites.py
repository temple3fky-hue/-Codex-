"""手工烟雾测试：验证 Unsplash/Pexels/Pixabay 提取和下载流程。"""
from __future__ import annotations

import asyncio

from core.config import load_settings
from core.task_manager import TaskManager

TEST_URLS = [
    "https://unsplash.com/photos/A-NVHPka9Rk",
    "https://www.pexels.com/photo/1108099/",
    "https://pixabay.com/photos/forest-fog-nature-trees-mystic-931706/",
]


async def main():
    settings = load_settings()
    logs = []

    def log(msg: str):
        logs.append(msg)
        print(msg)

    manager = TaskManager(settings, log_cb=log)
    await manager.run(TEST_URLS)


if __name__ == "__main__":
    asyncio.run(main())
