from pathlib import Path

import yaml

SETTINGS = "Settings"


class YamlTool:
    def __init__(self, path_to_config_file: Path):
        self.path_to_config_file = path_to_config_file

    def get_config(self):
        with open(self.path_to_config_file, "r") as file:
            data = yaml.safe_load(file)

        return data

    def get_settings(self):
        config = self.get_config()
        settings = config[SETTINGS]

        return settings

    def save_settings(self, data: dict):
        with open(self.path_to_config_file, "w") as file:
            yaml.dump(data, file, sort_keys=False)

    def update_a_setting(self, setting_name, new_value, config_section=SETTINGS):
        config = self.get_config()
        settings = config[config_section]
        settings[setting_name] = new_value
        self.save_settings(config)
