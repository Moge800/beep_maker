"""波形生成モジュールのテスト。"""

import numpy as np
import pytest

from src.config.constants import SAMPLE_RATE
from src.generator.waveforms import (
    generate_sawtooth_wave,
    generate_sine_wave,
    generate_square_wave,
    generate_sweep,
)


class TestGenerateSineWave:
    """正弦波生成のテスト。"""

    def test_length(self) -> None:
        """正弦波の長さが正しいことを確認。"""
        duration = 0.1
        wave = generate_sine_wave(frequency=440.0, duration=duration)
        expected_samples = int(SAMPLE_RATE * duration)
        assert len(wave) == expected_samples

    def test_amplitude_range(self) -> None:
        """正弦波の振幅が -1.0 〜 1.0 の範囲であることを確認。"""
        wave = generate_sine_wave(frequency=440.0, duration=0.1)
        assert np.all(wave >= -1.0)
        assert np.all(wave <= 1.0)

    def test_invalid_frequency(self) -> None:
        """不正な周波数でValueErrorが発生することを確認。"""
        with pytest.raises(ValueError, match="frequency must be positive"):
            generate_sine_wave(frequency=0, duration=0.1)
        with pytest.raises(ValueError, match="frequency must be positive"):
            generate_sine_wave(frequency=-100, duration=0.1)

    def test_invalid_duration(self) -> None:
        """不正な長さでValueErrorが発生することを確認。"""
        with pytest.raises(ValueError, match="duration must be positive"):
            generate_sine_wave(frequency=440, duration=0)
        with pytest.raises(ValueError, match="duration must be positive"):
            generate_sine_wave(frequency=440, duration=-0.1)


class TestGenerateSquareWave:
    """矩形波生成のテスト。"""

    def test_length(self) -> None:
        """矩形波の長さが正しいことを確認。"""
        duration = 0.1
        wave = generate_square_wave(frequency=440.0, duration=duration)
        expected_samples = int(SAMPLE_RATE * duration)
        assert len(wave) == expected_samples

    def test_amplitude_values(self) -> None:
        """矩形波の振幅が -1.0 または 1.0 であることを確認。"""
        wave = generate_square_wave(frequency=440.0, duration=0.1)
        unique_values = np.unique(wave)
        assert len(unique_values) == 2
        assert -1.0 in unique_values
        assert 1.0 in unique_values

    def test_invalid_duty(self) -> None:
        """不正なデューティ比でValueErrorが発生することを確認。"""
        with pytest.raises(ValueError, match="duty must be between"):
            generate_square_wave(frequency=440, duration=0.1, duty=0)
        with pytest.raises(ValueError, match="duty must be between"):
            generate_square_wave(frequency=440, duration=0.1, duty=1)


class TestGenerateSawtoothWave:
    """ノコギリ波生成のテスト。"""

    def test_length(self) -> None:
        """ノコギリ波の長さが正しいことを確認。"""
        duration = 0.1
        wave = generate_sawtooth_wave(frequency=440.0, duration=duration)
        expected_samples = int(SAMPLE_RATE * duration)
        assert len(wave) == expected_samples

    def test_amplitude_range(self) -> None:
        """ノコギリ波の振幅が -1.0 〜 1.0 の範囲であることを確認。"""
        wave = generate_sawtooth_wave(frequency=440.0, duration=0.1)
        assert np.all(wave >= -1.0)
        assert np.all(wave < 1.0)  # ノコギリ波は1.0に到達しない


class TestGenerateSweep:
    """スイープ生成のテスト。"""

    def test_length(self) -> None:
        """スイープの長さが正しいことを確認。"""
        duration = 0.1
        wave = generate_sweep(start_freq=200, end_freq=1000, duration=duration)
        expected_samples = int(SAMPLE_RATE * duration)
        assert len(wave) == expected_samples

    def test_amplitude_range(self) -> None:
        """スイープの振幅が -1.0 〜 1.0 の範囲であることを確認。"""
        wave = generate_sweep(start_freq=200, end_freq=1000, duration=0.1)
        assert np.all(wave >= -1.0)
        assert np.all(wave <= 1.0)

    def test_logarithmic_sweep(self) -> None:
        """対数スイープが生成できることを確認。"""
        wave = generate_sweep(
            start_freq=200, end_freq=1000, duration=0.1, logarithmic=True
        )
        assert len(wave) == int(SAMPLE_RATE * 0.1)

    def test_invalid_frequencies(self) -> None:
        """不正な周波数でValueErrorが発生することを確認。"""
        with pytest.raises(ValueError, match="start_freq must be positive"):
            generate_sweep(start_freq=0, end_freq=1000, duration=0.1)
        with pytest.raises(ValueError, match="end_freq must be positive"):
            generate_sweep(start_freq=200, end_freq=0, duration=0.1)
