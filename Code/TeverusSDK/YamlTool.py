from pathlib import Path

import yaml

SETTINGS = "Settings"


class YamlTool:
    def __init__(self, path_to_config_file: Path):
        self.path_to_config_file = path_to_config_file

    def read_yaml(self):
        with open(self.path_to_config_file, "r", encoding="utf-8") as file:
            data = yaml.safe_load(file)

        return data

    def save_yaml(self, data: dict):
        with open(self.path_to_config_file, "w", encoding="utf-8") as file:
            yaml.dump(data, file, sort_keys=False, allow_unicode=True)

    def get_section(self, section_name):
        file = self.read_yaml()
        section = file[section_name]

        return section

    def get_settings(self):
        config = self.read_yaml()
        settings = config[SETTINGS]

        return settings

    def update_a_setting(self, setting_name, new_value, config_section=SETTINGS):
        config = self.read_yaml()
        settings = config[config_section]
        settings[setting_name] = new_value
        self.save_yaml(config)
