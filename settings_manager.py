# settings_manager.py

import json
import os
from PyQt5.QtGui import QFont

class SettingsManager:
    def __init__(self, settings_file='settings.json'):
        self.settings_file = settings_file
        self.default_settings = {
            "theme": "Dark",  # 默认主题为“深色主题”
            "font_family": "Consolas",
            "font_size": 12,
            "show_line_numbers": True,
            "word_wrap": True,
            "last_opened_folder": "",  # 上次打开的文件夹
            "last_opened_file": ""     # 上次打开的.md文件
        }
        self.settings = self.load_settings()

    def load_settings(self):
        if not os.path.exists(self.settings_file):
            return self.default_settings.copy()
        try:
            with open(self.settings_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                # 确保所有必要的设置项都存在
                for key in self.default_settings:
                    if key not in settings:
                        settings[key] = self.default_settings[key]
                return settings
        except Exception as e:
            print(f"加载设置时发生错误: {e}")
            return self.default_settings.copy()

    def save_settings(self):
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"保存设置时发生错误: {e}")

    def get_theme(self):
        return self.settings.get("theme", self.default_settings["theme"])

    def set_theme(self, theme_name):
        self.settings["theme"] = theme_name
        self.save_settings()

    def get_font(self):
        return QFont(
            self.settings.get("font_family", self.default_settings["font_family"]),
            self.settings.get("font_size", self.default_settings["font_size"])
        )

    def set_font(self, font: QFont):
        self.settings["font_family"] = font.family()
        self.settings["font_size"] = font.pointSize()
        self.save_settings()

    def get_show_line_numbers(self):
        return self.settings.get("show_line_numbers", self.default_settings["show_line_numbers"])

    def set_show_line_numbers(self, show: bool):
        self.settings["show_line_numbers"] = show
        self.save_settings()

    def get_word_wrap(self):
        return self.settings.get("word_wrap", self.default_settings["word_wrap"])

    def set_word_wrap(self, wrap: bool):
        self.settings["word_wrap"] = wrap
        self.save_settings()

    # 新增方法：获取和设置上次打开的文件夹
    def get_last_opened_folder(self):
        return self.settings.get("last_opened_folder", self.default_settings["last_opened_folder"])

    def set_last_opened_folder(self, folder_path: str):
        self.settings["last_opened_folder"] = folder_path
        self.save_settings()

    # 新增方法：获取和设置上次打开的.md文件
    def get_last_opened_file(self):
        return self.settings.get("last_opened_file", self.default_settings["last_opened_file"])

    def set_last_opened_file(self, file_path: str):
        self.settings["last_opened_file"] = file_path
        self.save_settings()
