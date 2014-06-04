from .base import SettingsBase
import os


class EnvironmentSettings(SettingsBase):
    def get(self, path, default):
        return os.environ.get(path, default)
