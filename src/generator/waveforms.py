"""波形生成モジュール。

基本波形（正弦波、矩形波、ノコギリ波、スイープ）を生成する。
"""

import numpy as np

from src.config.constants import SAMPLE_RATE


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
    if frequency <= 0:
        raise ValueError(f"frequency must be positive, got {frequency}")
    if duration <= 0:
        raise ValueError(f"duration must be positive, got {duration}")

    num_samples = int(SAMPLE_RATE * duration)
    t = np.linspace(0, duration, num_samples, endpoint=False)
    return np.sin(2 * np.pi * frequency * t)


def generate_square_wave(
    frequency: float, duration: float, duty: float = 0.5
) -> np.ndarray:
    """矩形波を生成する。

    Args:
        frequency: 周波数（Hz）
        duration: 長さ（秒）
        duty: デューティ比（0.0 〜 1.0）

    Returns:
        正規化された矩形波のサンプル配列（-1.0 〜 1.0）

    Raises:
        ValueError: 引数が不正な場合
    """
    if frequency <= 0:
        raise ValueError(f"frequency must be positive, got {frequency}")
    if duration <= 0:
        raise ValueError(f"duration must be positive, got {duration}")
    if not 0 < duty < 1:
        raise ValueError(f"duty must be between 0 and 1, got {duty}")

    num_samples = int(SAMPLE_RATE * duration)
    t = np.linspace(0, duration, num_samples, endpoint=False)
    # 位相を計算し、デューティ比に基づいて矩形波を生成
    phase = (frequency * t) % 1.0
    return np.where(phase < duty, 1.0, -1.0)


def generate_sawtooth_wave(frequency: float, duration: float) -> np.ndarray:
    """ノコギリ波を生成する。

    Args:
        frequency: 周波数（Hz）
        duration: 長さ（秒）

    Returns:
        正規化されたノコギリ波のサンプル配列（-1.0 〜 1.0）

    Raises:
        ValueError: frequency または duration が正の値でない場合
    """
    if frequency <= 0:
        raise ValueError(f"frequency must be positive, got {frequency}")
    if duration <= 0:
        raise ValueError(f"duration must be positive, got {duration}")

    num_samples = int(SAMPLE_RATE * duration)
    t = np.linspace(0, duration, num_samples, endpoint=False)
    # 位相を計算し、-1 〜 1 の範囲にスケール
    phase = (frequency * t) % 1.0
    return 2.0 * phase - 1.0


def generate_sweep(
    start_freq: float, end_freq: float, duration: float, logarithmic: bool = False
) -> np.ndarray:
    """周波数スイープを生成する。

    Args:
        start_freq: 開始周波数（Hz）
        end_freq: 終了周波数（Hz）
        duration: 長さ（秒）
        logarithmic: Trueなら対数スイープ、Falseなら線形スイープ

    Returns:
        正規化されたスイープ波のサンプル配列（-1.0 〜 1.0）

    Raises:
        ValueError: 引数が不正な場合
    """
    if start_freq <= 0:
        raise ValueError(f"start_freq must be positive, got {start_freq}")
    if end_freq <= 0:
        raise ValueError(f"end_freq must be positive, got {end_freq}")
    if duration <= 0:
        raise ValueError(f"duration must be positive, got {duration}")

    num_samples = int(SAMPLE_RATE * duration)
    t = np.linspace(0, duration, num_samples, endpoint=False)

    if logarithmic:
        # 対数スイープ: 周波数が指数的に変化
        freq_ratio = end_freq / start_freq
        instantaneous_freq = start_freq * (freq_ratio ** (t / duration))
        phase = (
            2
            * np.pi
            * start_freq
            * duration
            / np.log(freq_ratio)
            * (freq_ratio ** (t / duration) - 1)
        )
    else:
        # 線形スイープ: 周波数が線形に変化
        freq_slope = (end_freq - start_freq) / duration
        phase = 2 * np.pi * (start_freq * t + 0.5 * freq_slope * t**2)

    return np.sin(phase)
