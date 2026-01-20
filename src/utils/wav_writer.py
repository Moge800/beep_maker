"""WAVファイル出力モジュール。

numpy配列をWAVファイルに書き出す。
"""

import wave
from pathlib import Path

import numpy as np

from src.config.constants import BIT_DEPTH, CHANNELS, MAX_AMPLITUDE, SAMPLE_RATE


def save_wav(samples: np.ndarray, output_path: Path | str) -> Path:
    """波形データをWAVファイルに保存する。

    Args:
        samples: 正規化された波形データ（-1.0 〜 1.0）
        output_path: 出力ファイルパス

    Returns:
        保存されたファイルのパス

    Raises:
        OSError: ファイル書き込みに失敗した場合
        ValueError: サンプルデータが空の場合
    """
    if len(samples) == 0:
        raise ValueError("samples must not be empty")

    output_path = Path(output_path)

    # 出力ディレクトリを作成
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # -1.0 〜 1.0 を 16bit signed int に変換
    # クリッピング処理
    clipped = np.clip(samples, -1.0, 1.0)
    int_samples = (clipped * MAX_AMPLITUDE).astype(np.int16)

    # WAVファイルに書き出し
    with wave.open(str(output_path), "wb") as wav_file:
        wav_file.setnchannels(CHANNELS)
        wav_file.setsampwidth(BIT_DEPTH // 8)  # bytes per sample
        wav_file.setframerate(SAMPLE_RATE)
        wav_file.writeframes(int_samples.tobytes())

    return output_path


def get_wav_info(file_path: Path | str) -> dict[str, int | float]:
    """WAVファイルの情報を取得する。

    Args:
        file_path: WAVファイルのパス

    Returns:
        WAVファイル情報の辞書（channels, sample_width, frame_rate, n_frames, duration_sec）

    Raises:
        OSError: ファイル読み込みに失敗した場合
    """
    file_path = Path(file_path)

    with wave.open(str(file_path), "rb") as wav_file:
        n_frames = wav_file.getnframes()
        frame_rate = wav_file.getframerate()

        return {
            "channels": wav_file.getnchannels(),
            "sample_width": wav_file.getsampwidth(),
            "frame_rate": frame_rate,
            "n_frames": n_frames,
            "duration_sec": n_frames / frame_rate,
        }
