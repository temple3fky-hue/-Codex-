"""SQLite 历史记录存储。"""
from __future__ import annotations

import aiosqlite

DB_PATH = "data/history.db"


async def init_db() -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS downloads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_url TEXT NOT NULL,
                media_url TEXT NOT NULL,
                media_type TEXT NOT NULL,
                filename TEXT NOT NULL,
                status TEXT NOT NULL,
                local_path TEXT,
                file_hash TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        await db.commit()


async def insert_history(record: dict) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            INSERT INTO downloads (source_url, media_url, media_type, filename, status, local_path, file_hash)
            VALUES (:source_url, :media_url, :media_type, :filename, :status, :local_path, :file_hash)
            """,
            record,
        )
        await db.commit()


async def list_history() -> list[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM downloads ORDER BY id DESC")
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]
