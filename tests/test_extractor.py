import unittest
from unittest.mock import patch

from core.extractor import InvalidURLError, UnsupportedPlatformError, extract_media, identify_platform
from models.schemas import AppSettings


class ExtractorTests(unittest.IsolatedAsyncioTestCase):
    async def test_supported_site_recognition(self):
        self.assertEqual(identify_platform("https://unsplash.com/photos/demo"), "supported")
        self.assertEqual(identify_platform("https://www.pexels.com/photo/123"), "supported")
        self.assertEqual(identify_platform("https://pixabay.com/photos/demo"), "supported")

    async def test_empty_or_invalid_url(self):
        self.assertEqual(identify_platform(""), "invalid")
        with self.assertRaises(InvalidURLError):
            await extract_media("", AppSettings(), html_provider=lambda _u: "")

    async def test_unsupported_platforms(self):
        for url in [
            "https://www.youtube.com/watch?v=abc",
            "https://www.instagram.com/p/abc",
            "https://x.com/user/status/1",
            "https://www.tumblr.com/post/1",
        ]:
            self.assertEqual(identify_platform(url), "deferred")
            with self.assertRaises(UnsupportedPlatformError):
                await extract_media(url, AppSettings(), html_provider=lambda _u: "")

    async def test_extract_with_mocked_parser_no_network(self):
        async def provider(_u):
            return "<html>dummy</html>"

        fake_tasks = []
        with patch("core.extractor._extract_images_from_html", return_value=fake_tasks):
            with self.assertRaises(Exception) as ctx:
                await extract_media("https://unsplash.com/photos/demo", AppSettings(), html_provider=provider)
            self.assertIn("未提取到图片资源", str(ctx.exception))

    async def test_download_fail_path_style_message(self):
        async def provider(_u):
            return "<html>dummy</html>"

        with patch("core.extractor._extract_images_from_html", side_effect=RuntimeError("mock parse fail")):
            with self.assertRaises(Exception) as ctx:
                await extract_media("https://unsplash.com/photos/demo", AppSettings(), html_provider=provider)
            self.assertIn("页面解析失败", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
