"""定数定義モジュール。

WAVフォーマット規定およびサウンド種別を定義する。
"""

from enum import Enum

# WAV フォーマット規定
SAMPLE_RATE: int = 16000  # Hz
BIT_DEPTH: int = 16  # bits
CHANNELS: int = 1  # mono
MAX_AMPLITUDE: int = 32767  # 16bit signed max

# 時間関連
FADE_DURATION_MS: int = 5  # ms
MAX_DURATION_SEC: float = 0.20  # seconds
MIN_DURATION_SEC: float = 0.05  # seconds


class SoundType(str, Enum):
    """サウンド種別。

    産業用ビープ音の8種類を定義。
    """

    OK = "ok"
    NG = "ng"
    WARN = "warn"
    CRIT = "crit"
    MOO = "moo"
    MEW = "mew"
    SCAN_OK = "scan_ok"
    SCAN_NG = "scan_ng"

    @classmethod
    def list_all(cls) -> list[str]:
        """全サウンド種別名をリストで返す。"""
        return [s.value for s in cls]
