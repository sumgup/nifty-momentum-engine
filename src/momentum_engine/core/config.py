from pathlib import Path
import yaml


class ConfigLoader:
    def __init__(self, config_path: str):
        self.path = Path(config_path)

    def load(self) -> dict:
        if not self.path.exists():
            raise FileNotFoundError(f"Config file not found: {self.path}")

        with open(self.path, "r") as f:
            return yaml.safe_load(f)