"""Tests of the demo configuration loader."""

import re

import pytest

from src.sentinella import config


def test_demo_config_loads():
    demo = config.load()
    assert demo.demo_rule.include <= set(config.CATEGORIES)
    assert demo.fragility.changes in config.FRAGILITY_CHANGES


def test_unknown_category_in_demo_rule_is_rejected(tmp_path):
    text = re.sub(
        r"^include = .*$",
        'include = ["Critical"]',
        config.CONFIG_PATH.read_text(),
        flags=re.MULTILINE,
    )
    path = tmp_path / "demo.toml"
    path.write_text(text)
    with pytest.raises(ValueError, match="Critical"):
        config.load(path)


def test_unknown_judgment_first_setting_is_rejected(tmp_path):
    text = re.sub(
        r"^judgment_first = .*$",
        'judgment_first = "sometimes"',
        config.CONFIG_PATH.read_text(),
        flags=re.MULTILINE,
    )
    path = tmp_path / "demo.toml"
    path.write_text(text)
    with pytest.raises(ValueError, match="sometimes"):
        config.load(path)
