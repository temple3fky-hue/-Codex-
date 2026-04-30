import unittest
from unittest.mock import AsyncMock

from core.task_manager import TaskManager
from models.schemas import AppSettings, DownloadTask


class TaskManagerTests(unittest.IsolatedAsyncioTestCase):
    async def test_logs_when_empty_url_results(self):
        logs = []
        downloader = type("D", (), {"download_tasks": AsyncMock(), "pause_flag": False, "stop_flag": False})()
        manager = TaskManager(AppSettings(), log_cb=logs.append, downloader=downloader)

        async def fake_extractor(_url, _settings):
            return []

        await manager.run(["https://unsplash.com/photos/demo"], extractor=fake_extractor)
        self.assertTrue(any("没有可下载资源" in line for line in logs))

    async def test_download_pipeline_called(self):
        logs = []
        downloader = type("D", (), {"download_tasks": AsyncMock(), "pause_flag": False, "stop_flag": False})()
        manager = TaskManager(AppSettings(), log_cb=logs.append, downloader=downloader)

        async def fake_extractor(_url, _settings):
            return [
                DownloadTask(
                    source_url="https://unsplash.com/photos/demo",
                    media_url="https://images.unsplash.com/photo-1.jpg",
                    media_type="image",
                    filename="photo-1.jpg",
                )
            ]

        await manager.run(["https://unsplash.com/photos/demo"], extractor=fake_extractor)
        downloader.download_tasks.assert_awaited_once()
        self.assertTrue(any("总任务数: 1" in line for line in logs))


if __name__ == "__main__":
    unittest.main()
