from pathlib import Path

import toml

config = toml.load(open(Path('.config.toml').absolute()))
