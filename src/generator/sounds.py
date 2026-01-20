"""サウンド種別ごとの生成ロジック。

8種類の産業用ビープ音を生成する。
"""

from dataclasses import dataclass
from typing import Callable

import numpy as np

from src.config.constants import SoundType
from src.generator.envelope import apply_fade, concatenate_with_silence
from src.generator.waveforms import generate_sine_wave, generate_sweep


@dataclass
class SoundConfig:
    """サウンド設定。"""

    name: str
    description: str
    generator: Callable[[], np.ndarray]


def _generate_ok() -> np.ndarray:
    """OK: 明るい短音・上昇系。

    800Hz → 1200Hz の短い上昇音（0.08秒）
    """
    wave = generate_sweep(800, 1200, 0.08)
    return apply_fade(wave, fade_in_ms=5, fade_out_ms=5)


def _generate_ng() -> np.ndarray:
    """NG: 下降・やや長め。

    600Hz → 300Hz の下降音（0.15秒）
    """
    wave = generate_sweep(600, 300, 0.15)
    return apply_fade(wave, fade_in_ms=5, fade_out_ms=10)


def _generate_warn() -> np.ndarray:
    """WARN: 同音2回で注意喚起。

    1000Hz の短音を2回（各0.05秒、間隔0.05秒）
    """
    beep = generate_sine_wave(1000, 0.05)
    beep = apply_fade(beep, fade_in_ms=3, fade_out_ms=3)
    return concatenate_with_silence([beep, beep], silence_ms=50)


def _generate_crit() -> np.ndarray:
    """CRIT: 低音3連で緊急性。

    400Hz の短音を3回（各0.05秒、間隔0.03秒）
    """
    beep = generate_sine_wave(400, 0.05)
    beep = apply_fade(beep, fade_in_ms=3, fade_out_ms=3)
    return concatenate_with_silence([beep, beep, beep], silence_ms=30)


def _generate_moo() -> np.ndarray:
    """MOO: 低域スイープで柔らかい通知。

    200Hz → 400Hz のゆるやかな上昇（0.15秒）
    """
    wave = generate_sweep(200, 400, 0.15)
    return apply_fade(wave, fade_in_ms=10, fade_out_ms=10)


def _generate_mew() -> np.ndarray:
    """MEW: 高域スイープで軽い通知。

    1500Hz → 2000Hz の軽い上昇（0.10秒）
    """
    wave = generate_sweep(1500, 2000, 0.10)
    return apply_fade(wave, fade_in_ms=5, fade_out_ms=5)


def _generate_scan_ok() -> np.ndarray:
    """SCAN_OK: 極短で鋭い成功音。

    1500Hz の極短音（0.05秒）
    """
    wave = generate_sine_wave(1500, 0.05)
    return apply_fade(wave, fade_in_ms=2, fade_out_ms=3)


def _generate_scan_ng() -> np.ndarray:
    """SCAN_NG: 低短音で即時失敗。

    300Hz の短音（0.08秒）
    """
    wave = generate_sine_wave(300, 0.08)
    return apply_fade(wave, fade_in_ms=3, fade_out_ms=5)


# サウンド設定マップ
SOUND_CONFIGS: dict[SoundType, SoundConfig] = {
    SoundType.OK: SoundConfig(
        name="ok",
        description="成功通知 - 明るい短音・上昇系",
        generator=_generate_ok,
    ),
    SoundType.NG: SoundConfig(
        name="ng",
        description="失敗通知 - 下降・やや長め",
        generator=_generate_ng,
    ),
    SoundType.WARN: SoundConfig(
        name="warn",
        description="警告 - 同音2回で注意喚起",
        generator=_generate_warn,
    ),
    SoundType.CRIT: SoundConfig(
        name="crit",
        description="緊急警告 - 低音3連で緊急性",
        generator=_generate_crit,
    ),
    SoundType.MOO: SoundConfig(
        name="moo",
        description="柔らかい通知 - 低域スイープ",
        generator=_generate_moo,
    ),
    SoundType.MEW: SoundConfig(
        name="mew",
        description="軽い通知 - 高域スイープ",
        generator=_generate_mew,
    ),
    SoundType.SCAN_OK: SoundConfig(
        name="scan_ok",
        description="スキャン成功 - 極短で鋭い成功音",
        generator=_generate_scan_ok,
    ),
    SoundType.SCAN_NG: SoundConfig(
        name="scan_ng",
        description="スキャン失敗 - 低短音で即時失敗",
        generator=_generate_scan_ng,
    ),
}


def generate_sound(sound_type: SoundType) -> np.ndarray:
    """指定されたサウンド種別の波形を生成する。

    Args:
        sound_type: サウンド種別

    Returns:
        生成された波形のサンプル配列（-1.0 〜 1.0）

    Raises:
        ValueError: 未知のサウンド種別の場合
    """
    if sound_type not in SOUND_CONFIGS:
        raise ValueError(f"Unknown sound type: {sound_type}")

    config = SOUND_CONFIGS[sound_type]
    return config.generator()
