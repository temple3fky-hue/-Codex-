"""文件处理工具。"""
from __future__ import annotations

import hashlib
from pathlib import Path
from urllib.parse import urlparse


def guess_filename(url: str, fallback_prefix: str = "media") -> str:
    path = Path(urlparse(url).path)
    name = path.name or fallback_prefix
    if "." not in name:
        return f"{name}.bin"
    return name


def file_hash(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def ensure_unique(path: Path) -> Path:
    if not path.exists():
        return path
    stem, suffix = path.stem, path.suffix
    idx = 1
    while True:
        candidate = path.with_name(f"{stem}_{idx}{suffix}")
        if not candidate.exists():
            return candidate
        idx += 1
