from pathlib import Path

import toml


def get_config():
    return toml.load(open(Path('.config.toml').absolute()))
