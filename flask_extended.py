import yaml

from flask import Flask as BaseFlask, Config as BaseConfig
from ons_ras_common.ras_config import ras_config


class Config(BaseConfig):
    """Flask config enhanced with a `from_yaml` method."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dependency = {}
        self.feature = {}

    def from_yaml(self, config_file):
        with open(config_file) as f:
            c = ras_config.from_yaml_file(config_file)

        for k, v in c.items():
            self[k] = v

        for k, v in c.dependencies():
            self.dependency[k] = v

        for k, v in c.features():
            self.feature[k] = v

        # for key in c.iterkeys():
        #     self[key] = c[key]


class Flask(BaseFlask):
    """Extended version of `Flask` that implements custom config class"""

    def make_config(self, instance_relative=False):
        root_path = self.root_path
        if instance_relative:
            root_path = self.instance_path
        return Config(root_path, self.default_config)
