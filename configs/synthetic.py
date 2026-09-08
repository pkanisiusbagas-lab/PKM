"""Synthetic config — re-export dari src.synthetic.config + default path proyek."""

from src.synthetic.config import Config, load_config, setup_logging

SYNTHETIC_CONFIG = {
    "specs_dir": "data/synthetic/specs",
    "generated_dir": "data/synthetic/generated",
    "default_output": "data/synthetic/generated/dataset.jsonl",
}

__all__ = ["SYNTHETIC_CONFIG", "Config", "load_config", "setup_logging"]
