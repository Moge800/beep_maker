"""エンベロープモジュール。

フェードイン/アウト、ADSRエンベロープを適用する。
"""

import numpy as np

from src.config.constants import FADE_DURATION_MS, SAMPLE_RATE


def apply_fade(
    samples: np.ndarray,
    fade_in_ms: float = FADE_DURATION_MS,
    fade_out_ms: float = FADE_DURATION_MS,
) -> np.ndarray:
    """フェードイン/アウトを適用する。

    Args:
        samples: 入力サンプル配列
        fade_in_ms: フェードイン時間（ミリ秒）
        fade_out_ms: フェードアウト時間（ミリ秒）

    Returns:
        フェード適用後のサンプル配列
    """
    result = samples.copy()
    num_samples = len(result)

    # フェードインのサンプル数を計算
    fade_in_samples = int(SAMPLE_RATE * fade_in_ms / 1000)
    fade_in_samples = min(fade_in_samples, num_samples // 2)

    # フェードアウトのサンプル数を計算
    fade_out_samples = int(SAMPLE_RATE * fade_out_ms / 1000)
    fade_out_samples = min(fade_out_samples, num_samples // 2)

    # フェードイン適用（線形）
    if fade_in_samples > 0:
        fade_in_curve = np.linspace(0, 1, fade_in_samples)
        result[:fade_in_samples] *= fade_in_curve

    # フェードアウト適用（線形）
    if fade_out_samples > 0:
        fade_out_curve = np.linspace(1, 0, fade_out_samples)
        result[-fade_out_samples:] *= fade_out_curve

    return result


def apply_adsr(
    samples: np.ndarray,
    attack_ms: float,
    decay_ms: float,
    sustain_level: float,
    release_ms: float,
) -> np.ndarray:
    """ADSRエンベロープを適用する。

    Args:
        samples: 入力サンプル配列
        attack_ms: アタック時間（ミリ秒）
        decay_ms: ディケイ時間（ミリ秒）
        sustain_level: サステインレベル（0.0 〜 1.0）
        release_ms: リリース時間（ミリ秒）

    Returns:
        ADSR適用後のサンプル配列

    Raises:
        ValueError: sustain_level が範囲外の場合
    """
    if not 0 <= sustain_level <= 1:
        raise ValueError(f"sustain_level must be between 0 and 1, got {sustain_level}")

    result = samples.copy()
    num_samples = len(result)

    # 各フェーズのサンプル数を計算
    attack_samples = int(SAMPLE_RATE * attack_ms / 1000)
    decay_samples = int(SAMPLE_RATE * decay_ms / 1000)
    release_samples = int(SAMPLE_RATE * release_ms / 1000)

    # サステインのサンプル数（残り）
    sustain_samples = max(
        0, num_samples - attack_samples - decay_samples - release_samples
    )

    # エンベロープ配列を構築
    envelope = np.zeros(num_samples)
    pos = 0

    # Attack: 0 → 1
    if attack_samples > 0 and pos < num_samples:
        end = min(pos + attack_samples, num_samples)
        envelope[pos:end] = np.linspace(0, 1, end - pos)
        pos = end

    # Decay: 1 → sustain_level
    if decay_samples > 0 and pos < num_samples:
        end = min(pos + decay_samples, num_samples)
        envelope[pos:end] = np.linspace(1, sustain_level, end - pos)
        pos = end

    # Sustain: sustain_level を維持
    if sustain_samples > 0 and pos < num_samples:
        end = min(pos + sustain_samples, num_samples)
        envelope[pos:end] = sustain_level
        pos = end

    # Release: sustain_level → 0
    if release_samples > 0 and pos < num_samples:
        end = num_samples
        envelope[pos:end] = np.linspace(sustain_level, 0, end - pos)

    result *= envelope
    return result


def concatenate_with_silence(
    segments: list[np.ndarray], silence_ms: float = 0
) -> np.ndarray:
    """複数の波形を無音区間を挟んで連結する。

    Args:
        segments: 波形セグメントのリスト
        silence_ms: セグメント間の無音時間（ミリ秒）

    Returns:
        連結された波形配列
    """
    if not segments:
        return np.array([], dtype=np.float64)

    if silence_ms <= 0:
        return np.concatenate(segments)

    silence_samples = int(SAMPLE_RATE * silence_ms / 1000)
    silence = np.zeros(silence_samples)

    result_parts: list[np.ndarray] = []
    for i, segment in enumerate(segments):
        result_parts.append(segment)
        if i < len(segments) - 1:
            result_parts.append(silence)

    return np.concatenate(result_parts)
