# theme.py

from PyQt5.QtGui import QColor

# 定义所有可用的主题
THEMES = {
    "Light": {
        "palette": {
            "Window": "#ffffff",
            "WindowText": "#000000",
            "Base": "#ffffff",
            "AlternateBase": "#f5f5f5",
            "ToolTipBase": "#ffffff",
            "ToolTipText": "#000000",
            "Text": "#000000",
            "Button": "#f0f0f0",
            "ButtonText": "#000000",
            "BrightText": "#ff0000",
            "Highlight": "#1e90ff",
            "HighlightedText": "#ffffff",
        },
        "highlighter": {
            "header": "#1e90ff",
            "bold": "#000000",
            "italic": "#000000",
            "code": "#dcdcdc",
            "link": "#1e90ff",
            "blockquote": "#808080",
            "unordered_list": "#228B22",
            "ordered_list": "#228B22",
        },
        "code_block": {
            "background": "#f5f5f5",
            "text": "#000000",
        }
    },
    "Dark": {
        "palette": {
            "Window": "#2b2b2b",
            "WindowText": "#dcdcdc",
            "Base": "#2b2b2b",
            "AlternateBase": "#1e1e1e",
            "ToolTipBase": "#ffffff",
            "ToolTipText": "#000000",
            "Text": "#dcdcdc",
            "Button": "#3c3c3c",
            "ButtonText": "#dcdcdc",
            "BrightText": "#ff0000",
            "Highlight": "#1e90ff",
            "HighlightedText": "#ffffff",
        },
        "highlighter": {
            "header": "#1e90ff",
            "bold": "#ffffff",
            "italic": "#ffffff",
            "code": "#dcdcdc",
            "link": "#1e90ff",
            "blockquote": "#a9a9a9",
            "unordered_list": "#32cd32",
            "ordered_list": "#32cd32",
        },
        "code_block": {
            "background": "#3c3c3c",
            "text": "#dcdcdc",
        }
    },
    "Solarized Light": {
        "palette": {
            "Window": "#fdf6e3",
            "WindowText": "#657b83",
            "Base": "#fdf6e3",
            "AlternateBase": "#eee8d5",
            "ToolTipBase": "#fdf6e3",
            "ToolTipText": "#657b83",
            "Text": "#657b83",
            "Button": "#eee8d5",
            "ButtonText": "#657b83",
            "BrightText": "#dc322f",
            "Highlight": "#268bd2",
            "HighlightedText": "#ffffff",
        },
        "highlighter": {
            "header": "#268bd2",
            "bold": "#657b83",
            "italic": "#657b83",
            "code": "#2aa198",
            "link": "#268bd2",
            "blockquote": "#859900",
            "unordered_list": "#b58900",
            "ordered_list": "#b58900",
        },
        "code_block": {
            "background": "#eee8d5",
            "text": "#657b83",
        }
    },
    "Solarized Dark": {
        "palette": {
            "Window": "#002b36",
            "WindowText": "#839496",
            "Base": "#073642",
            "AlternateBase": "#586e75",
            "ToolTipBase": "#002b36",
            "ToolTipText": "#839496",
            "Text": "#839496",
            "Button": "#586e75",
            "ButtonText": "#839496",
            "BrightText": "#dc322f",
            "Highlight": "#268bd2",
            "HighlightedText": "#ffffff",
        },
        "highlighter": {
            "header": "#2aa198",
            "bold": "#839496",
            "italic": "#839496",
            "code": "#93a1a1",
            "link": "#2aa198",
            "blockquote": "#859900",
            "unordered_list": "#b58900",
            "ordered_list": "#b58900",
        },
        "code_block": {
            "background": "#586e75",
            "text": "#839496",
        }
    }
}

def get_theme_names():
    """返回所有可用的主题名称。"""
    return list(THEMES.keys())

def get_theme(theme_name):
    """根据主题名称返回主题配置。"""
    return THEMES.get(theme_name, THEMES["Light"])
