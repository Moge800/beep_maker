"""WAVファイル出力モジュールのテスト。"""

import tempfile
from pathlib import Path

import numpy as np
import pytest

from src.config.constants import BIT_DEPTH, CHANNELS, SAMPLE_RATE
from src.utils.wav_writer import get_wav_info, save_wav


class TestSaveWav:
    """WAVファイル保存のテスト。"""

    def test_save_creates_file(self) -> None:
        """ファイルが作成されることを確認。"""
        samples = np.sin(np.linspace(0, 2 * np.pi, 1600))
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test.wav"
            result = save_wav(samples, output_path)
            assert result.exists()
            assert result == output_path

    def test_save_creates_parent_directory(self) -> None:
        """親ディレクトリが自動作成されることを確認。"""
        samples = np.sin(np.linspace(0, 2 * np.pi, 1600))
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "subdir" / "test.wav"
            result = save_wav(samples, output_path)
            assert result.exists()

    def test_wav_format_correct(self) -> None:
        """WAVフォーマットが正しいことを確認。"""
        samples = np.sin(np.linspace(0, 2 * np.pi, 1600))
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test.wav"
            save_wav(samples, output_path)

            info = get_wav_info(output_path)
            assert info["channels"] == CHANNELS
            assert info["sample_width"] == BIT_DEPTH // 8
            assert info["frame_rate"] == SAMPLE_RATE
            assert info["n_frames"] == 1600

    def test_empty_samples_raises_error(self) -> None:
        """空のサンプルでValueErrorが発生することを確認。"""
        samples = np.array([])
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test.wav"
            with pytest.raises(ValueError, match="samples must not be empty"):
                save_wav(samples, output_path)

    def test_clipping_applied(self) -> None:
        """クリッピングが適用されることを確認（範囲外の値）。"""
        # 範囲外の値を含むサンプル
        samples = np.array([2.0, -2.0, 0.5, -0.5])
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test.wav"
            # エラーなく保存できることを確認
            result = save_wav(samples, output_path)
            assert result.exists()


class TestGetWavInfo:
    """WAVファイル情報取得のテスト。"""

    def test_get_info_returns_correct_values(self) -> None:
        """正しい情報が返されることを確認。"""
        samples = np.sin(np.linspace(0, 2 * np.pi, 1600))
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test.wav"
            save_wav(samples, output_path)

            info = get_wav_info(output_path)
            assert "channels" in info
            assert "sample_width" in info
            assert "frame_rate" in info
            assert "n_frames" in info
            assert "duration_sec" in info
            assert info["duration_sec"] == pytest.approx(0.1, rel=0.01)
