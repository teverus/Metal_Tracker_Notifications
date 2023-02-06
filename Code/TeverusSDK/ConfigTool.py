from configparser import ConfigParser
from pathlib import Path

SETTINGS = "Settings"


class ConfigTool:
    def __init__(self, path_to_config_file: Path):
        self.path_to_config_file = path_to_config_file

    def get_config(self):
        config = ConfigParser()
        config.read(self.path_to_config_file)

        return config

    def get_settings(self):
        config = self.get_config()
        settings = config[SETTINGS]

        return settings

    def save_settings(self, config: ConfigParser):
        with open(self.path_to_config_file, "w") as configfile:
            config.write(configfile)

    def update_a_setting(self, setting_name, new_value, config_section=SETTINGS):
        config = self.get_config()
        settings = config[config_section]
        settings[setting_name] = new_value
        self.save_settings(config)
