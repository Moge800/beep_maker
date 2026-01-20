"""beep-maker CLI エントリーポイント。

industrial-beep 用 WAV ビープ音生成ツール。
"""

import sys
from pathlib import Path

# srcディレクトリをパスに追加
sys.path.insert(0, str(Path(__file__).parent))

from src.cli.commands import app

if __name__ == "__main__":
    app()
