import os
import configparser
import json


class Config:
    _instance = None
    _config = None

    def __init__(self):
        self.init_dir()

    def __new__(cls, filename=os.path.join(os.path.dirname(__file__),  'config.ini')):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._config = configparser.ConfigParser()
            cls._config.read(filename, encoding="utf-8")

        return cls._instance

    def get(self, section, option):
        if not self._config.has_section(section):
            raise Exception(f'Section {section} not found in the config file')
        if not self._config.has_option(section, option):
            raise Exception(f'Option {option} not found in the section {section}')
        try:
            return json.loads(self._config.get(section, option))
        except:
            return self._config.get(section, option)

    def init_dir(self):
        output_path = self._config.get("report", "output_path")
        if output_path:
            os.makedirs(output_path, exist_ok=True)

        tmp_output_path = self._config.get("report", "tmp_output_path")
        if tmp_output_path:
            os.makedirs(tmp_output_path, exist_ok=True)

        template = self._config.get("report", "template")
        if template:
            os.makedirs(template, exist_ok=True)

        log = self._config.get("report", "log")
        if log:
            os.makedirs(log, exist_ok=True)


config = Config()

if __name__ == '__main__':

    # 使用示例
    value = config.get('report', 'img_type')
    print(f'Value: {value}')
