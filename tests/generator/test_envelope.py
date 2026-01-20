"""エンベロープモジュールのテスト。"""

import numpy as np
import pytest

from src.config.constants import SAMPLE_RATE
from src.generator.envelope import apply_adsr, apply_fade, concatenate_with_silence


class TestApplyFade:
    """フェード適用のテスト。"""

    def test_fade_in_starts_at_zero(self) -> None:
        """フェードイン適用後、先頭が0に近いことを確認。"""
        samples = np.ones(1600)  # 0.1秒 @ 16kHz
        result = apply_fade(samples, fade_in_ms=10, fade_out_ms=0)
        assert result[0] == pytest.approx(0.0, abs=0.01)

    def test_fade_out_ends_at_zero(self) -> None:
        """フェードアウト適用後、末尾が0に近いことを確認。"""
        samples = np.ones(1600)
        result = apply_fade(samples, fade_in_ms=0, fade_out_ms=10)
        assert result[-1] == pytest.approx(0.0, abs=0.01)

    def test_fade_preserves_length(self) -> None:
        """フェード適用後も長さが変わらないことを確認。"""
        samples = np.ones(1600)
        result = apply_fade(samples, fade_in_ms=5, fade_out_ms=5)
        assert len(result) == len(samples)

    def test_no_modification_to_original(self) -> None:
        """元の配列が変更されないことを確認。"""
        samples = np.ones(1600)
        original_copy = samples.copy()
        apply_fade(samples, fade_in_ms=5, fade_out_ms=5)
        np.testing.assert_array_equal(samples, original_copy)


class TestApplyADSR:
    """ADSRエンベロープのテスト。"""

    def test_attack_starts_at_zero(self) -> None:
        """アタック開始時が0であることを確認。"""
        samples = np.ones(3200)  # 0.2秒 @ 16kHz
        result = apply_adsr(
            samples, attack_ms=10, decay_ms=10, sustain_level=0.7, release_ms=10
        )
        assert result[0] == pytest.approx(0.0, abs=0.01)

    def test_release_ends_at_zero(self) -> None:
        """リリース終了時が0に近いことを確認。"""
        samples = np.ones(3200)
        result = apply_adsr(
            samples, attack_ms=10, decay_ms=10, sustain_level=0.7, release_ms=10
        )
        assert result[-1] == pytest.approx(0.0, abs=0.01)

    def test_invalid_sustain_level(self) -> None:
        """不正なサステインレベルでValueErrorが発生することを確認。"""
        samples = np.ones(1600)
        with pytest.raises(ValueError, match="sustain_level must be between"):
            apply_adsr(
                samples, attack_ms=10, decay_ms=10, sustain_level=1.5, release_ms=10
            )
        with pytest.raises(ValueError, match="sustain_level must be between"):
            apply_adsr(
                samples, attack_ms=10, decay_ms=10, sustain_level=-0.1, release_ms=10
            )


class TestConcatenateWithSilence:
    """波形連結のテスト。"""

    def test_concatenate_without_silence(self) -> None:
        """無音なしで連結できることを確認。"""
        seg1 = np.ones(100)
        seg2 = np.ones(100) * 2
        result = concatenate_with_silence([seg1, seg2], silence_ms=0)
        assert len(result) == 200

    def test_concatenate_with_silence(self) -> None:
        """無音ありで連結できることを確認。"""
        seg1 = np.ones(100)
        seg2 = np.ones(100)
        silence_samples = int(SAMPLE_RATE * 50 / 1000)  # 50ms
        result = concatenate_with_silence([seg1, seg2], silence_ms=50)
        assert len(result) == 200 + silence_samples

    def test_empty_segments(self) -> None:
        """空のセグメントリストで空配列が返ることを確認。"""
        result = concatenate_with_silence([], silence_ms=50)
        assert len(result) == 0

    def test_single_segment(self) -> None:
        """単一セグメントでそのまま返ることを確認。"""
        seg = np.ones(100)
        result = concatenate_with_silence([seg], silence_ms=50)
        assert len(result) == 100
