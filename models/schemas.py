"""数据模型定义。"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class DownloadTask:
    """下载任务。"""

    source_url: str
    media_url: str
    media_type: str
    filename: str
    status: str = "pending"
    progress: float = 0.0
    retries: int = 0
    error: str = ""
    local_path: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class AppSettings:
    """应用配置。"""

    download_dir: str = "downloads"
    concurrency: int = 5
    max_retries: int = 3
    speed_limit_kb: int = 0
    auto_rename: bool = True
    skip_existing: bool = True
    max_file_size_mb: int = 512
    user_agent_mode: str = "random"
    proxy: str = ""
    cookies_file: str = "data/cookies.json"
    file_types: str = "jpg,jpeg,png,webp,gif,mp4,webm,m3u8"
    min_delay_ms: int = 300
    max_delay_ms: int = 1500


@dataclass
class HistoryRecord:
    source_url: str
    media_url: str
    media_type: str
    filename: str
    status: str
    local_path: str
    file_hash: Optional[str]
    created_at: datetime
