"""Flet GUI。"""
from __future__ import annotations

import asyncio

import flet as ft

from core.config import load_settings, save_settings
from core.database import init_db
from core.exporter import export_history_csv, export_history_excel
from core.task_manager import TaskManager


def run_app():
    ft.app(target=main)


def main(page: ft.Page):
    page.title = "图片/视频爬虫下载器"
    page.theme_mode = ft.ThemeMode.DARK
    page.window_width = 1200
    page.window_height = 850
    settings = load_settings()

    log_box = ft.TextField(multiline=True, min_lines=8, max_lines=12, read_only=True)
    url_input = ft.TextField(
        label="输入 URL（每行一个）",
        multiline=True,
        min_lines=4,
        hint_text="https://unsplash.com/...\nhttps://www.youtube.com/...",
    )
    progress_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("文件名")),
            ft.DataColumn(ft.Text("进度")),
            ft.DataColumn(ft.Text("状态")),
        ],
        rows=[],
    )

    rows_map = {}

    def log(msg: str):
        log_box.value = (log_box.value or "") + msg + "\n"
        page.update()

    def on_progress(task):
        if task.media_url not in rows_map:
            row = ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(task.filename)),
                    ft.DataCell(ft.Text("0%")),
                    ft.DataCell(ft.Text(task.status)),
                ]
            )
            rows_map[task.media_url] = row
            progress_table.rows.append(row)
        row = rows_map[task.media_url]
        row.cells[1].content.value = f"{task.progress * 100:.1f}%"
        row.cells[2].content.value = task.status
        page.update()

    manager = TaskManager(settings, log_cb=log, progress_cb=on_progress)

    async def start_workflow(_):
        urls = [line.strip() for line in (url_input.value or "").splitlines() if line.strip()]
        if not urls:
            page.snack_bar = ft.SnackBar(ft.Text("链接无效：请至少输入一个 URL"), open=True)
            page.update()
            log("链接无效：请至少输入一个 URL")
            return
        progress_table.rows.clear()
        rows_map.clear()
        await manager.run(urls)

    def start_click(_):
        page.run_task(start_workflow, None)

    def pause_click(_):
        manager.pause()
        log("已暂停")

    def resume_click(_):
        manager.resume()
        log("已恢复")

    def stop_click(_):
        manager.stop()
        log("已停止")

    async def export_csv(_):
        path = await export_history_csv()
        log(f"CSV 已导出: {path}")

    async def export_xlsx(_):
        path = await export_history_excel()
        log(f"Excel 已导出: {path}")

    settings_view = ft.Column(
        [
            ft.Text("设置", size=22, weight=ft.FontWeight.BOLD),
            ft.TextField(label="下载目录", value=settings.download_dir, on_change=lambda e: setattr(settings, "download_dir", e.control.value)),
            ft.TextField(label="并发数", value=str(settings.concurrency), on_change=lambda e: setattr(settings, "concurrency", int(e.control.value or "5"))),
            ft.TextField(label="代理 (http://ip:port 或 socks5://...)", value=settings.proxy, on_change=lambda e: setattr(settings, "proxy", e.control.value)),
            ft.Switch(label="自动重命名", value=settings.auto_rename, on_change=lambda e: setattr(settings, "auto_rename", e.control.value)),
            ft.Switch(label="跳过已存在", value=settings.skip_existing, on_change=lambda e: setattr(settings, "skip_existing", e.control.value)),
            ft.ElevatedButton("保存设置", on_click=lambda e: (save_settings(settings), log("设置已保存"))),
        ]
    )

    main_view = ft.Column(
        [
            ft.Text("图片/视频批量爬虫下载器", size=28, weight=ft.FontWeight.BOLD),
            ft.Text("当前稳定支持：Unsplash / Pexels / Pixabay", color=ft.Colors.GREEN_300),
            url_input,
            ft.Row([
                ft.ElevatedButton("开始提取并下载", on_click=start_click),
                ft.OutlinedButton("暂停", on_click=pause_click),
                ft.OutlinedButton("恢复", on_click=resume_click),
                ft.OutlinedButton("停止", on_click=stop_click),
                ft.OutlinedButton("导出CSV", on_click=lambda e: page.run_task(export_csv, None)),
                ft.OutlinedButton("导出Excel", on_click=lambda e: page.run_task(export_xlsx, None)),
            ]),
            ft.Text("下载进度", size=20),
            ft.Container(content=progress_table, expand=True),
            ft.Text("实时日志", size=20),
            log_box,
        ],
        expand=True,
    )

    tabs = ft.Tabs(
        selected_index=0,
        tabs=[
            ft.Tab(text="主界面", content=main_view),
            ft.Tab(text="设置", content=settings_view),
        ],
        expand=True,
    )

    asyncio.run(init_db())
    page.add(tabs)
