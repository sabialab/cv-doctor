"""CV-Doctor CLI 入口

使用 Typer 框架构建命令行界面。
"""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel

from src import __version__

app = typer.Typer(
    name="cv-doctor",
    help="🩺 CV-Doctor 简历对症下药 — LLM 驱动的简历深度优化工具",
    add_completion=False,
)
console = Console()


def version_callback(value: bool) -> None:
    if value:
        console.print(f"CV-Doctor v{__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        False, "--version", "-v", callback=version_callback, is_eager=True,
        help="显示版本号",
    ),
) -> None:
    """🩺 CV-Doctor 简历对症下药 — LLM 驱动的简历深度优化工具"""
    pass


# ==================== optimize 命令 ====================


@app.command()
def optimize(
    resume: Path = typer.Argument(..., help="简历文件路径 (PDF/DOCX/MD)"),
    jd: str | None = typer.Option(None, "--jd", help="JD 文本内容"),
    jd_file: Path | None = typer.Option(None, "--jd-file", help="JD 文件路径"),
    jd_url: str | None = typer.Option(None, "--jd-url", help="JD 链接（BOSS直聘等）"),
    output_format: str = typer.Option("pdf", "--format", "-f", help="输出格式: pdf/docx/markdown"),
    output_dir: Path | None = typer.Option(None, "--output", "-o", help="输出目录"),
) -> None:
    """通用优化模式 — 上传简历 + JD，快速优化"""
    console.print(Panel.fit(
        "[bold blue]🩺 CV-Doctor 通用优化模式[/bold blue]",
        subtitle="简历 + JD → 优化后简历",
    ))

    # TODO: Phase 1 实现
    console.print("[yellow]⚠️  此功能正在开发中（Phase 1）[/yellow]")
    console.print(f"简历: {resume}")
    console.print(f"JD: {jd or jd_file or jd_url}")
    console.print(f"输出格式: {output_format}")


# ==================== target 命令 ====================


@app.command()
def target(
    resume: Path = typer.Argument(..., help="简历文件路径 (PDF/DOCX/MD)"),
    company: str = typer.Option(..., "--company", "-c", help="目标公司名称"),
    position: str = typer.Option(..., "--position", "-p", help="目标岗位名称"),
    city: str | None = typer.Option(None, "--city", help="目标城市"),
    output_format: str = typer.Option("pdf", "--format", "-f", help="输出格式: pdf/docx/markdown"),
    output_dir: Path | None = typer.Option(None, "--output", "-o", help="输出目录"),
) -> None:
    """对症下药模式 ⭐ — 针对具体公司+岗位深度优化"""
    console.print(Panel.fit(
        "[bold red]🎯 CV-Doctor 对症下药模式[/bold red]",
        subtitle=f"目标: {company} - {position}",
    ))

    # TODO: Phase 2 实现
    console.print("[yellow]⚠️  此功能正在开发中（Phase 2）[/yellow]")
    console.print(f"简历: {resume}")
    console.print(f"目标公司: {company}")
    console.print(f"目标岗位: {position}")
    console.print(f"目标城市: {city or '不限'}")
    console.print(f"输出格式: {output_format}")


# ==================== score 命令 ====================


@app.command()
def score(
    resume: Path = typer.Argument(..., help="简历文件路径 (PDF/DOCX/MD)"),
    jd: str | None = typer.Option(None, "--jd", help="JD 文本内容"),
    jd_file: Path | None = typer.Option(None, "--jd-file", help="JD 文件路径"),
) -> None:
    """ATS 评分 — 评估简历与 JD 的匹配度"""
    console.print(Panel.fit(
        "[bold green]📊 CV-Doctor ATS 评分[/bold green]",
        subtitle="简历 vs JD 匹配度分析",
    ))

    # TODO: Phase 1 实现
    console.print("[yellow]⚠️  此功能正在开发中（Phase 1）[/yellow]")
    console.print(f"简历: {resume}")
    console.print(f"JD: {jd or jd_file}")


# ==================== company 命令 ====================


@app.command()
def company(
    name: str = typer.Argument(..., help="公司名称"),
    position: str | None = typer.Option(None, "--position", "-p", help="岗位名称（可选）"),
) -> None:
    """公司画像 — 查看目标公司的深度分析"""
    console.print(Panel.fit(
        "[bold cyan]🏢 CV-Doctor 公司画像[/bold cyan]",
        subtitle=name,
    ))

    # TODO: Phase 2 实现
    console.print("[yellow]⚠️  此功能正在开发中（Phase 2）[/yellow]")
    console.print(f"公司: {name}")
    if position:
        console.print(f"岗位: {position}")


# ==================== parse 命令 ====================


@app.command()
def parse(
    resume: Path = typer.Argument(..., help="简历文件路径 (PDF/DOCX/MD)"),
    output_format: str = typer.Option("json", "--format", "-f", help="输出格式: json/yaml/text"),
) -> None:
    """简历解析 — 查看简历解析结果（调试用）"""
    console.print(Panel.fit(
        "[bold magenta]📋 CV-Doctor 简历解析[/bold magenta]",
        subtitle=str(resume),
    ))

    # TODO: Phase 1 实现
    console.print("[yellow]⚠️  此功能正在开发中（Phase 1）[/yellow]")
    console.print(f"简历: {resume}")
    console.print(f"输出格式: {output_format}")


# ==================== config 命令 ====================


@app.command("config")
def config_cmd(
    key: str = typer.Argument(..., help="配置项名称 (如 llm.provider)"),
    value: str | None = typer.Argument(None, help="配置值（不填则查看当前值）"),
) -> None:
    """配置管理 — 查看或修改配置"""
    from src.config import config

    if value is None:
        # 查看配置
        keys = key.split(".")
        obj = config
        for k in keys:
            if hasattr(obj, k):
                obj = getattr(obj, k)
            else:
                console.print(f"[red]❌ 配置项不存在: {key}[/red]")
                raise typer.Exit(1)
        console.print(f"{key} = {obj}")
    else:
        # TODO: 实现配置写入
        console.print(f"[yellow]⚠️  配置写入功能正在开发中[/yellow]")
        console.print(f"设置 {key} = {value}")


if __name__ == "__main__":
    app()
