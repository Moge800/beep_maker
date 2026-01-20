"""サウンド生成モジュールのテスト。"""

import numpy as np
import pytest

from src.config.constants import (
    MAX_DURATION_SEC,
    MIN_DURATION_SEC,
    SAMPLE_RATE,
    SoundType,
)
from src.generator.sounds import SOUND_CONFIGS, generate_sound


class TestGenerateSound:
    """サウンド生成のテスト。"""

    @pytest.mark.parametrize("sound_type", list(SoundType))
    def test_all_sounds_generate_without_error(self, sound_type: SoundType) -> None:
        """全8種のサウンドが例外なく生成できることを確認。"""
        wave = generate_sound(sound_type)
        assert isinstance(wave, np.ndarray)
        assert len(wave) > 0

    @pytest.mark.parametrize("sound_type", list(SoundType))
    def test_all_sounds_amplitude_range(self, sound_type: SoundType) -> None:
        """全サウンドの振幅が -1.0 〜 1.0 の範囲であることを確認。"""
        wave = generate_sound(sound_type)
        assert np.all(wave >= -1.0)
        assert np.all(wave <= 1.0)

    @pytest.mark.parametrize("sound_type", list(SoundType))
    def test_all_sounds_duration_within_spec(self, sound_type: SoundType) -> None:
        """全サウンドの長さが仕様範囲内（0.05〜0.20秒）であることを確認。"""
        wave = generate_sound(sound_type)
        duration_sec = len(wave) / SAMPLE_RATE
        # 連結音（warn, crit）は無音区間を含むため少し余裕を持たせる
        assert duration_sec >= MIN_DURATION_SEC
        assert duration_sec <= MAX_DURATION_SEC + 0.05  # 余裕


class TestSoundConfigs:
    """サウンド設定のテスト。"""

    def test_all_sound_types_have_config(self) -> None:
        """全サウンド種別に設定が存在することを確認。"""
        for sound_type in SoundType:
            assert sound_type in SOUND_CONFIGS

    def test_config_has_required_fields(self) -> None:
        """各設定に必須フィールドが存在することを確認。"""
        for sound_type, config in SOUND_CONFIGS.items():
            assert config.name == sound_type.value
            assert len(config.description) > 0
            assert callable(config.generator)


class TestSoundTypeEnum:
    """SoundType列挙型のテスト。"""

    def test_list_all(self) -> None:
        """list_allが全種別を返すことを確認。"""
        all_sounds = SoundType.list_all()
        assert len(all_sounds) == 8
        assert "ok" in all_sounds
        assert "ng" in all_sounds
        assert "warn" in all_sounds
        assert "crit" in all_sounds
        assert "moo" in all_sounds
        assert "mew" in all_sounds
        assert "scan_ok" in all_sounds
        assert "scan_ng" in all_sounds
