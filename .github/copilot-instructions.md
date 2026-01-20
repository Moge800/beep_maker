# GitHub Copilot Instructions

## プロジェクト概要
industrial-beep ライブラリ用の WAV ビープ音を生成する CLI ツール。産業現場の騒音下でも識別しやすい音を、numpy + wave で生成し、typer + rich でリッチな CLI 体験を提供する。

## 技術スタック
- **Python**: 3.13
- **パッケージマネージャ**: uv
- **音声生成**: numpy, wave（標準ライブラリ）
- **CLI フレームワーク**: typer, rich
- **開発ツール**: Black, Ruff, pytest, pytest-cov

## プロジェクト構造
```
beep_maker/
├── main.py                    # CLI エントリーポイント
├── pyproject.toml
├── .python-version            # 3.13
├── .gitignore
├── src/
│   ├── cli/
│   │   └── commands.py        # typer コマンド定義
│   ├── generator/
│   │   ├── waveforms.py       # 波形生成（正弦波、矩形波等）
│   │   ├── envelope.py        # エンベロープ（フェードイン/アウト）
│   │   └── sounds.py          # サウンド種別ごとの生成ロジック
│   ├── config/
│   │   └── constants.py       # 定数定義（周波数、サンプリングレート等）
│   └── utils/
│       └── wav_writer.py      # WAV ファイル出力
├── assets/                    # 出力先（gitignore 対象）
│   ├── ok.wav
│   ├── ng.wav
│   └── ...
├── tests/                     # テストコード
│   ├── generator/
│   ├── cli/
│   └── utils/
├── .github/
│   ├── copilot-instructions.md
│   └── workflows/
│       ├── lint.yml
│       └── test.yml
└── README.md
```

**モジュール責務分離**:
- `commands.py`: CLI コマンド定義、引数パース、rich 出力
- `waveforms.py`: 基本波形生成（正弦波、矩形波、ノコギリ波）
- `envelope.py`: フェードイン/アウト、ADSR エンベロープ
- `sounds.py`: サウンド種別ごとの周波数・波形・長さ定義
- `constants.py`: サンプリングレート、ビット深度等の定数
- `wav_writer.py`: numpy 配列から WAV ファイルへの書き出し

## CLI コマンド仕様

### 個別生成
```bash
# 単一サウンド生成
python main.py generate ok
python main.py generate ng --output-dir ./output

# 出力先指定
python main.py generate warn --output-dir /path/to/dir
```

### 一括生成
```bash
# 全8種を一括生成
python main.py generate-all
python main.py generate-all --output-dir ./assets
```

### オプション
| オプション | 短縮形 | 説明 | デフォルト |
|-----------|--------|------|-----------|
| `--output-dir` | `-o` | 出力ディレクトリ | `./assets` |
| `--force` | `-f` | 既存ファイル上書き | `False` |
| `--verbose` | `-v` | 詳細ログ出力 | `False` |

## サウンド仕様

### 対象サウンド種別
| 種別 | 用途 | 音デザイン |
|------|------|-----------|
| `ok` | 成功通知 | 明るい短音・上昇系 |
| `ng` | 失敗通知 | 下降・やや長め |
| `warn` | 警告 | 同音2回で注意喚起 |
| `crit` | 緊急警告 | 低音3連で緊急性 |
| `moo` | 柔らかい通知 | 低域スイープ |
| `mew` | 軽い通知 | 高域スイープ |
| `scan_ok` | スキャン成功 | 極短で鋭い成功音 |
| `scan_ng` | スキャン失敗 | 低短音で即時失敗 |

### WAV フォーマット規定
| 項目 | 値 |
|------|-----|
| サンプリングレート | 16,000 Hz |
| ビット深度 | 16bit PCM |
| チャンネル | モノラル |
| 長さ | 0.05 〜 0.20 秒 |
| フェード | 5 〜 10 ms |
| ファイルサイズ | 1音あたり数 KB |

### 定数定義例
```python
# src/config/constants.py
SAMPLE_RATE = 16000          # Hz
BIT_DEPTH = 16               # bits
CHANNELS = 1                 # mono
FADE_DURATION_MS = 5         # ms
MAX_DURATION_SEC = 0.20      # seconds
MIN_DURATION_SEC = 0.05      # seconds
```

## コーディング規約

### 1. 型ヒントは必須
```python
# Good
def generate_sine_wave(frequency: float, duration: float) -> np.ndarray:
    return np.sin(2 * np.pi * frequency * np.linspace(0, duration, int(SAMPLE_RATE * duration)))

# Bad
def generate_sine_wave(frequency, duration):
    return np.sin(2 * np.pi * frequency * np.linspace(0, duration, int(SAMPLE_RATE * duration)))
```

### 2. エラーハンドリング
- `Exception` の汎用捕捉は避ける
- 具体的な例外を指定: `ValueError`, `OSError`, `IOError` など
- CLI では `typer.Exit()` でエラー終了
```python
# Good
from typer import Exit
from rich.console import Console

console = Console()

try:
    save_wav(samples, output_path)
except OSError as e:
    console.print(f"[red]Error:[/red] Failed to save WAV file: {e}")
    raise Exit(code=1)

# Bad
except Exception as e:
    pass
```

### 3. マジックナンバーは定数化
```python
# Good
from src.config.constants import SAMPLE_RATE, FADE_DURATION_MS

fade_samples = int(SAMPLE_RATE * FADE_DURATION_MS / 1000)

# Bad
fade_samples = int(16000 * 5 / 1000)
```

### 4. グローバル変数は避ける
- シングルトンが必要な場合はクラス属性を使用
- `global` キーワードは使わない
- 設定値は `constants.py` で管理

### 5. インポート順序
```python
# 標準ライブラリ
import wave
from pathlib import Path

# サードパーティ
import numpy as np
import typer
from rich.console import Console
from rich.progress import Progress

# ローカル
from src.config.constants import SAMPLE_RATE
from src.generator.waveforms import generate_sine_wave
```

### 6. type: ignore は最小限に
- 型を正しく定義すれば不要なはず
- やむを得ない場合のみ使用し、理由をコメント

### 7. ファイルエンコーディング
- **PowerShell スクリプト (`.ps1`)**: UTF-8 BOM 付き（Microsoft 推奨）
- **その他すべてのファイル**: UTF-8 BOM なし

## テスト

### テスト駆動開発（TDD）の推奨
**新機能追加時は必ずテストも同時作成する**

#### テストの配置
```
tests/
├── generator/           # 波形生成のテスト
│   ├── test_waveforms.py
│   ├── test_envelope.py
│   └── test_sounds.py
├── cli/                 # CLI コマンドのテスト
│   └── test_commands.py
└── utils/               # ユーティリティのテスト
    └── test_wav_writer.py
```

#### テスト作成ルール
1. **新しい関数を追加** → 対応するテストを `tests/` に作成
2. **ビジネスロジック変更** → 既存テストを更新 + 新ケース追加
3. **バグ修正** → 再現テストを追加してから修正

#### 波形生成テストの例
```python
import numpy as np
import pytest
from src.generator.waveforms import generate_sine_wave
from src.config.constants import SAMPLE_RATE

def test_generate_sine_wave_length():
    """正弦波の長さが正しいことを確認"""
    duration = 0.1
    wave = generate_sine_wave(frequency=440.0, duration=duration)
    expected_samples = int(SAMPLE_RATE * duration)
    assert len(wave) == expected_samples

def test_generate_sine_wave_amplitude():
    """正弦波の振幅が -1.0 〜 1.0 の範囲であることを確認"""
    wave = generate_sine_wave(frequency=440.0, duration=0.1)
    assert np.all(wave >= -1.0)
    assert np.all(wave <= 1.0)
```

#### テスト実行コマンド
```bash
# 全テスト実行
pytest tests/ -v

# 特定のテストファイルのみ
pytest tests/generator/test_waveforms.py -v

# カバレッジ計測
pytest --cov=src tests/
```

#### テストの命名規則
- ファイル: `test_*.py`
- クラス: `Test*`（例: `TestWaveformGenerator`）
- 関数: `test_*`（例: `test_generate_sine_wave_length`）

## コード品質
- Black: フォーマッター（自動整形）
- Ruff: Linter（静的解析）
- Pylance: VSCode 型チェック
- 全てセットアップ済み（`.vscode/settings.json`）

## 命名規則
- クラス: `PascalCase`（例: `WaveformGenerator`, `SoundConfig`）
- 関数/変数: `snake_case`（例: `generate_sine_wave`, `sample_rate`）
- 定数: `UPPER_SNAKE_CASE`（例: `SAMPLE_RATE`, `MAX_DURATION_SEC`）
- プライベート: `_leading_underscore`（例: `_apply_fade`, `_normalize`）

## ドキュメント
- Docstring: Google Style
- 型ヒントで大部分は自己文書化
- 複雑なロジックにはインラインコメント

```python
def generate_sine_wave(frequency: float, duration: float) -> np.ndarray:
    """正弦波を生成する。

    Args:
        frequency: 周波数（Hz）
        duration: 長さ（秒）

    Returns:
        正規化された正弦波のサンプル配列（-1.0 〜 1.0）

    Raises:
        ValueError: frequency または duration が正の値でない場合
    """
```

## 定期メンテナンス手順

### 大きな変更時・仕事終わりのチェックリスト

#### 1. 全スキャンによるテスト項目チェック
大きな機能追加や1日の開発終了時に、テストの過不足をチェック:

**チェック対象**:
- [ ] 新規追加した関数にテストがあるか
- [ ] 修正したロジックのテストケースが十分か
- [ ] 新しい波形生成関数にユニットテストがあるか
- [ ] エラーハンドリングのテストが網羅されているか

#### 2. コミット前の最終チェック
```bash
# 1. 全テスト実行
pytest tests/ -v --tb=short

# 2. Lint 確認
ruff check src/ tests/
black --check src/ tests/

# 3. 型チェック (VSCode Pylance)
# エラーパネルで確認

# 4. 変更差分確認
git status
git diff

# 5. コミット
git add .
git commit -m "feat: <変更内容の要約>"
git push origin main
```

## よくある問題と解決策

### numpy 配列の型エラー
- `np.int16` へのキャストを忘れずに
- 正規化（-1.0 〜 1.0）後に 32767 を掛けて int16 に変換

### WAV ファイルが無音
- サンプル値が 0 になっていないか確認
- `np.int16` への変換前に正規化されているか確認

### CLI が認識されない
- `main.py` に typer アプリが正しく定義されているか確認
- `python main.py --help` で確認

### assets フォルダがない
- 初回実行時に自動作成するか、`mkdir -p assets` で作成

---

**このプロジェクトは industrial-beep ライブラリのサウンドアセット生成ツールです。質問や改善提案は歓迎します！**
