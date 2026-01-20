"""CLIコマンド定義モジュール。

typer + rich でリッチなCLI体験を提供する。
"""

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from src.config.constants import SoundType
from src.generator.sounds import SOUND_CONFIGS, generate_sound
from src.utils.wav_writer import save_wav

app = typer.Typer(
    name="beep-maker",
    help="industrial-beep 用 WAV ビープ音生成 CLI ツール",
    add_completion=False,
)

console = Console()

# デフォルト出力ディレクトリ
DEFAULT_OUTPUT_DIR = Path("./assets")


@app.command()
def generate(
    sound_type: Annotated[
        str,
        typer.Argument(
            help=f"サウンド種別: {', '.join(SoundType.list_all())}",
        ),
    ],
    output_dir: Annotated[
        Path,
        typer.Option(
            "--output-dir",
            "-o",
            help="出力ディレクトリ",
        ),
    ] = DEFAULT_OUTPUT_DIR,
    force: Annotated[
        bool,
        typer.Option(
            "--force",
            "-f",
            help="既存ファイルを上書き",
        ),
    ] = False,
    verbose: Annotated[
        bool,
        typer.Option(
            "--verbose",
            "-v",
            help="詳細ログ出力",
        ),
    ] = False,
) -> None:
    """単一サウンドを生成する。"""
    # サウンド種別の検証
    try:
        sound = SoundType(sound_type.lower())
    except ValueError:
        console.print(f"[red]Error:[/red] 不明なサウンド種別: {sound_type}")
        console.print(f"有効な種別: {', '.join(SoundType.list_all())}")
        raise typer.Exit(code=1) from None

    output_path = output_dir / f"{sound.value}.wav"

    # 既存ファイルチェック
    if output_path.exists() and not force:
        console.print(f"[yellow]Warning:[/yellow] {output_path} は既に存在します")
        console.print("上書きするには --force オプションを使用してください")
        raise typer.Exit(code=1)

    # 生成処理
    try:
        if verbose:
            console.print(f"[dim]生成中: {sound.value}[/dim]")

        samples = generate_sound(sound)
        save_wav(samples, output_path)

        console.print(f"[green]✓[/green] {output_path} を生成しました")

    except OSError as e:
        console.print(f"[red]Error:[/red] ファイル書き込みに失敗: {e}")
        raise typer.Exit(code=1) from None


@app.command("generate-all")
def generate_all(
    output_dir: Annotated[
        Path,
        typer.Option(
            "--output-dir",
            "-o",
            help="出力ディレクトリ",
        ),
    ] = DEFAULT_OUTPUT_DIR,
    force: Annotated[
        bool,
        typer.Option(
            "--force",
            "-f",
            help="既存ファイルを上書き",
        ),
    ] = False,
    verbose: Annotated[
        bool,
        typer.Option(
            "--verbose",
            "-v",
            help="詳細ログ出力",
        ),
    ] = False,
) -> None:
    """全8種のサウンドを一括生成する。"""
    console.print(f"[bold]出力先:[/bold] {output_dir.absolute()}")
    console.print()

    success_count = 0
    skip_count = 0
    error_count = 0

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("生成中...", total=len(SoundType))

        for sound_type in SoundType:
            output_path = output_dir / f"{sound_type.value}.wav"

            # 既存ファイルチェック
            if output_path.exists() and not force:
                if verbose:
                    console.print(
                        f"[yellow]⏭[/yellow] {sound_type.value}: スキップ（既存）"
                    )
                skip_count += 1
                progress.advance(task)
                continue

            try:
                progress.update(task, description=f"生成中: {sound_type.value}")

                samples = generate_sound(sound_type)
                save_wav(samples, output_path)

                if verbose:
                    console.print(f"[green]✓[/green] {sound_type.value}: 生成完了")

                success_count += 1

            except OSError as e:
                console.print(f"[red]✗[/red] {sound_type.value}: エラー - {e}")
                error_count += 1

            progress.advance(task)

    # 結果サマリー
    console.print()
    console.print("[bold]結果:[/bold]")
    console.print(f"  [green]成功:[/green] {success_count}")
    if skip_count > 0:
        console.print(f"  [yellow]スキップ:[/yellow] {skip_count}")
    if error_count > 0:
        console.print(f"  [red]エラー:[/red] {error_count}")

    if error_count > 0:
        raise typer.Exit(code=1)


@app.command("list")
def list_sounds() -> None:
    """利用可能なサウンド種別を一覧表示する。"""
    table = Table(title="サウンド種別一覧")
    table.add_column("種別", style="cyan")
    table.add_column("説明", style="white")

    for sound_type in SoundType:
        config = SOUND_CONFIGS[sound_type]
        table.add_row(sound_type.value, config.description)

    console.print(table)


@app.callback()
def main(
    version: Annotated[
        bool | None,
        typer.Option(
            "--version",
            "-V",
            help="バージョンを表示",
            is_eager=True,
        ),
    ] = None,
) -> None:
    """industrial-beep 用 WAV ビープ音生成 CLI ツール。"""
    if version:
        console.print("beep-maker version 0.1.0")
        raise typer.Exit()
