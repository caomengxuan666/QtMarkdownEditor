# markdown_editor.py

import sys
import os
import shutil
import re
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QAction, QFileDialog,
    QMessageBox, QSplitter, QListWidget, QToolBar, QColorDialog,
    QFontDialog, QDialog, QPushButton, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QInputDialog
)
from PyQt5.QtCore import Qt, QTimer, QUrl
from PyQt5.QtGui import QFont, QTextCursor, QColor, QPalette, QTextCharFormat, QSyntaxHighlighter, QIcon
from PyQt5.QtWebEngineWidgets import QWebEngineView
import markdown
from settings_manager import SettingsManager  # 导入设置管理器
import theme  # 导入主题模块

class MarkdownHighlighter(QSyntaxHighlighter):
    # 定义块状态
    CODE_BLOCK = 1  # 当前块在代码块中
    CODE_BLOCK_CPP = 2
    CODE_BLOCK_PYTHON = 3
    # 可以根据需要添加更多语言的状态

    def __init__(self, parent=None, theme_colors=None):
        super(MarkdownHighlighter, self).__init__(parent)
        self.highlighting_rules = []
        self.set_theme(theme_colors or theme.get_theme("Light")["highlighter"])

        # 定义语言特定的高亮规则
        self.language_rules = {
            'cpp': self.get_cpp_rules(),
            'python': self.get_python_rules(),
            # 可以添加更多语言
        }

    def set_theme(self, theme_colors):
        """根据当前主题设置高亮颜色。"""
        self.highlighting_rules = []

        # 标题（# 标题）
        header_format = QTextCharFormat()
        header_format.setForeground(QColor(theme_colors["header"]))
        header_format.setFontWeight(QFont.Bold)
        header_patterns = [r'^(#{1,6})\s.*']
        for pattern in header_patterns:
            self.highlighting_rules.append((re.compile(pattern), header_format))

        # 粗体（**文本** 或 __文本__）
        bold_format = QTextCharFormat()
        bold_format.setFontWeight(QFont.Bold)
        bold_format.setForeground(QColor(theme_colors["bold"]))
        bold_patterns = [r'\*\*(.*?)\*\*', r'__(.*?)__']
        for pattern in bold_patterns:
            self.highlighting_rules.append((re.compile(pattern), bold_format))

        # 斜体（*文本* 或 _文本_）
        italic_format = QTextCharFormat()
        italic_format.setFontItalic(True)
        italic_format.setForeground(QColor(theme_colors["italic"]))
        italic_patterns = [r'\*(.*?)\*', r'_(.*?)_']
        for pattern in italic_patterns:
            self.highlighting_rules.append((re.compile(pattern), italic_format))

        # 链接（[文本](链接)）
        link_format = QTextCharFormat()
        link_format.setForeground(QColor(theme_colors["link"]))
        link_format.setFontUnderline(True)
        link_patterns = [r'\[([^\]]+)\]\(([^)]+)\)']
        for pattern in link_patterns:
            self.highlighting_rules.append((re.compile(pattern), link_format))

        # 引用（> 引用文本）
        blockquote_format = QTextCharFormat()
        blockquote_format.setForeground(QColor(theme_colors["blockquote"]))
        blockquote_patterns = [r'^>\s.*']
        for pattern in blockquote_patterns:
            self.highlighting_rules.append((re.compile(pattern), blockquote_format))

        # 无序列表（最多两级嵌套）
        unordered_list_format = QTextCharFormat()
        unordered_list_format.setForeground(QColor(theme_colors["unordered_list"]))
        unordered_list_patterns = [r'^-\s.*', r'^\s+-\s.*']  # 支持一级和二级
        for pattern in unordered_list_patterns:
            self.highlighting_rules.append((re.compile(pattern), unordered_list_format))

        # 有序列表（最多两级嵌套）
        ordered_list_format = QTextCharFormat()
        ordered_list_format.setForeground(QColor(theme_colors["ordered_list"]))
        ordered_list_patterns = [r'^\d+\.\s.*', r'^\s+\d+\.\s.*']  # 支持一级和二级
        for pattern in ordered_list_patterns:
            self.highlighting_rules.append((re.compile(pattern), ordered_list_format))

        # 代码块（```lang 和 ```）
        self.code_block_start_pattern = re.compile(r'^```(\w+)?')
        self.code_block_end_pattern = re.compile(r'^```$')

    def get_cpp_rules(self):
        """定义C++语法高亮规则"""
        rules = []
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#0000FF"))  # 蓝色
        keyword_format.setFontWeight(QFont.Bold)
        keywords = [
            'int', 'float', 'double', 'char', 'bool', 'void', 'return',
            'if', 'else', 'for', 'while', 'do', 'switch', 'case', 'break',
            'continue', 'class', 'struct', 'public', 'private', 'protected',
            'namespace', 'using', 'std', 'include', 'define'
        ]
        keyword_pattern = r'\b(' + '|'.join(keywords) + r')\b'
        rules.append((re.compile(keyword_pattern), keyword_format))

        # 字符串
        string_format = QTextCharFormat()
        string_format.setForeground(QColor("#008000"))  # 绿色
        rules.append((re.compile(r'".*?"'), string_format))
        rules.append((re.compile(r"'.*?'"), string_format))

        # 注释
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#808080"))  # 灰色
        rules.append((re.compile(r'//.*'), comment_format))
        rules.append((re.compile(r'/\*.*\*/'), comment_format))

        return rules

    def get_python_rules(self):
        """定义Python语法高亮规则"""
        rules = []
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#0000FF"))  # 蓝色
        keyword_format.setFontWeight(QFont.Bold)
        keywords = [
            'def', 'return', 'if', 'else', 'elif', 'for', 'while', 'break',
            'continue', 'class', 'import', 'from', 'as', 'try', 'except',
            'finally', 'with', 'lambda', 'pass', 'raise', 'global', 'nonlocal',
            'assert', 'yield', 'del', 'in', 'is', 'and', 'or', 'not'
        ]
        keyword_pattern = r'\b(' + '|'.join(keywords) + r')\b'
        rules.append((re.compile(keyword_pattern), keyword_format))

        # 字符串
        string_format = QTextCharFormat()
        string_format.setForeground(QColor("#008000"))  # 绿色
        rules.append((re.compile(r'".*?"'), string_format))
        rules.append((re.compile(r"'.*?'"), string_format))

        # 注释
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#808080"))  # 灰色
        rules.append((re.compile(r'#.*'), comment_format))

        return rules

    def highlightBlock(self, text):
        if self.previousBlockState() not in [self.CODE_BLOCK, self.CODE_BLOCK_CPP, self.CODE_BLOCK_PYTHON]:
            match = self.code_block_start_pattern.match(text)
            if match:
                language = match.group(1)
                if language == 'cpp':
                    self.setCurrentBlockState(self.CODE_BLOCK_CPP)
                elif language == 'python':
                    self.setCurrentBlockState(self.CODE_BLOCK_PYTHON)
                else:
                    self.setCurrentBlockState(self.CODE_BLOCK)  # 通用代码块
                # 设置整行格式（代码块标识符的格式）
                code_block_format = QTextCharFormat()
                code_block_format.setForeground(QColor("#888888"))  # 设置代码块标识符颜色
                self.setFormat(0, len(text), code_block_format)
                return  # 代码块标识符单独处理，直接返回

        # 检查代码块的结束标识符 ```
        if self.previousBlockState() in [self.CODE_BLOCK, self.CODE_BLOCK_CPP, self.CODE_BLOCK_PYTHON]:
            if self.code_block_end_pattern.match(text):
                self.setCurrentBlockState(0)  # 退出代码块状态
                code_block_format = QTextCharFormat()
                code_block_format.setForeground(QColor("#888888"))  # 设置代码块标识符颜色
                self.setFormat(0, len(text), code_block_format)
                return  # 代码块结束标识符单独处理，直接返回
            else:
                # 处于代码块中时，应用特定语言的高亮规则
                language = None
                if self.previousBlockState() == self.CODE_BLOCK_CPP:
                    language = 'cpp'
                elif self.previousBlockState() == self.CODE_BLOCK_PYTHON:
                    language = 'python'

                # 应用语言特定规则
                if language and language in self.language_rules:
                    for pattern, fmt in self.language_rules[language]:
                        for match in pattern.finditer(text):
                            start, end = match.span()
                            self.setFormat(start, end - start, fmt)
                return  # 如果是代码块内部，处理完后直接返回

        # 如果不在代码块中，应用常规 Markdown 高亮规则
        for pattern, fmt in self.highlighting_rules:
            for match in pattern.finditer(text):
                start, end = match.span()
                self.setFormat(start, end - start, fmt)


class InsertCodeBlockDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("选择编程语言")
        self.setGeometry(100, 100, 300, 100)
        self.selected_language = None

        layout = QVBoxLayout()

        label = QLabel("选择代码块的编程语言:")
        layout.addWidget(label)

        self.language_combo = QComboBox()
        self.language_combo.addItems(["None", "cpp", "python", "java", "javascript", "csharp", "ruby", "go", "swift", "kotlin"])
        layout.addWidget(self.language_combo)

        button_layout = QHBoxLayout()
        insert_button = QPushButton("插入")
        insert_button.clicked.connect(self.insert_code_block)
        cancel_button = QPushButton("取消")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(insert_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def insert_code_block(self):
        language = self.language_combo.currentText()
        if language == "None":
            language = ""
        self.selected_language = language
        self.accept()

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("编辑器设置")
        self.setGeometry(100, 100, 400, 200)
        self.parent_editor = parent  # 引用主窗口

        self.settings_manager = parent.settings_manager  # 获取设置管理器

        layout = QVBoxLayout()

        # 主题选择
        theme_layout = QHBoxLayout()
        theme_label = QLabel("选择主题:")
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(theme.get_theme_names())  # 动态加载主题名称
        current_theme = self.settings_manager.get_theme()
        index = self.theme_combo.findText(current_theme if current_theme in theme.get_theme_names() else "Light")
        self.theme_combo.setCurrentIndex(index if index >= 0 else 0)
        self.theme_combo.currentIndexChanged.connect(self.change_theme)
        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(self.theme_combo)
        layout.addLayout(theme_layout)

        # 字体设置按钮
        self.font_btn = QPushButton("选择全局字体")
        self.font_btn.clicked.connect(self.choose_font)
        layout.addWidget(self.font_btn)

        self.setLayout(layout)

    def change_theme(self, index):
        try:
            theme_name = self.theme_combo.currentText()
            self.settings_manager.set_theme(theme_name)
            self.parent_editor.apply_theme(theme_name)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"切换主题时发生错误: {e}")

    def choose_font(self):
        try:
            # 获取当前全局字体
            current_font = self.settings_manager.get_font()

            # 打开字体选择对话框
            font, ok = QFontDialog.getFont(current_font, self, "选择全局字体")
            if ok:
                # 设置全局字体
                self.settings_manager.set_font(font)
                QApplication.setFont(font)

                # 重新更新预览区以应用新的字体
                self.parent_editor.update_preview()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"设置字体时发生错误: {e}")

class MarkdownEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cmx的 Markdown 编辑器")
        self.setGeometry(100, 100, 1400, 800)
        self.current_file = None
        self.current_folder = None
        # 设置图标
        self.setWindowIcon(QIcon("./wyw.ico"))



        # 初始化设置管理器
        self.settings_manager = SettingsManager()

        # 初始化防抖定时器
        self.preview_update_timer = QTimer()
        self.preview_update_timer.setSingleShot(True)
        self.preview_update_timer.timeout.connect(self._perform_update_preview)


        self.initUI()
        self.init_auto_save()
        # 加载上次打开的文件夹和文件
        self.load_last_session()

    def _perform_update_preview(self):
        self.update_preview()

    def load_last_session(self):
        last_folder = self.settings_manager.get_last_opened_folder()
        last_file = self.settings_manager.get_last_opened_file()

        if last_folder and os.path.isdir(last_folder):
            self.current_folder = last_folder
            self.populate_file_list(last_folder)

        if last_file and os.path.isfile(last_file):
            self.load_file(last_file)

    def initUI(self):
        try:
            # 创建菜单栏
            menubar = self.menuBar()
            file_menu = menubar.addMenu('&文件')
            settings_menu = menubar.addMenu('&设置')

            # 新建文件
            new_action = QAction('&新建', self)
            new_action.setShortcut('Ctrl+N')
            new_action.triggered.connect(self.new_file)
            file_menu.addAction(new_action)

            # 打开文件夹
            open_folder_action = QAction('&打开文件夹', self)
            open_folder_action.setShortcut('Ctrl+Shift+O')
            open_folder_action.triggered.connect(self.open_folder)
            file_menu.addAction(open_folder_action)

            # 打开文件
            open_action = QAction('&打开文件', self)
            open_action.setShortcut('Ctrl+O')
            open_action.triggered.connect(self.open_file)
            file_menu.addAction(open_action)

            # 保存文件
            save_action = QAction('&保存', self)
            save_action.setShortcut('Ctrl+S')
            save_action.triggered.connect(self.save_file)
            file_menu.addAction(save_action)

            # 插入图片
            insert_image_action = QAction('&插入图片', self)
            insert_image_action.setShortcut('Ctrl+I')
            insert_image_action.triggered.connect(self.insert_image)
            file_menu.addAction(insert_image_action)

            # 退出
            exit_action = QAction('&退出', self)
            exit_action.setShortcut('Ctrl+Q')
            exit_action.triggered.connect(self.close)
            file_menu.addAction(exit_action)

            delete_action = QAction("&删除文件", self)
            delete_action.setShortcut('Ctrl+D')
            delete_action.triggered.connect(self.del_file)
            file_menu.addAction(delete_action)

            # 设置菜单
            settings_action = QAction('&编辑器设置', self)
            settings_action.triggered.connect(self.open_settings)
            settings_menu.addAction(settings_action)

            # 创建工具栏
            self.toolbar = QToolBar("工具栏")
            self.addToolBar(self.toolbar)

            # 添加工具栏按钮
            bold_action = QAction('加粗', self)
            bold_action.triggered.connect(self.make_bold)
            self.toolbar.addAction(bold_action)

            italic_action = QAction('斜体', self)
            italic_action.triggered.connect(self.make_italic)
            self.toolbar.addAction(italic_action)

            heading_action = QAction('标题', self)
            heading_action.triggered.connect(self.make_heading)
            self.toolbar.addAction(heading_action)

            list_action = QAction('列表', self)
            list_action.triggered.connect(self.make_list)
            self.toolbar.addAction(list_action)

            image_action = QAction('图片', self)
            image_action.triggered.connect(self.insert_image)
            self.toolbar.addAction(image_action)

            # 添加插入代码块按钮
            code_block_action = QAction('代码块', self)
            code_block_action.triggered.connect(self.insert_code_block)
            self.toolbar.addAction(code_block_action)

            # 创建左侧文件列表
            self.file_list = QListWidget()
            self.file_list.itemClicked.connect(self.load_selected_file)

            # 创建编辑区和预览区
            splitter = QSplitter(Qt.Horizontal)

            # 左侧文件列表
            splitter.addWidget(self.file_list)

            # 右侧编辑和预览
            right_splitter = QSplitter(Qt.Vertical)

            # 编辑区
            self.editor = QTextEdit()
            current_font = self.settings_manager.get_font()
            self.editor.setFont(current_font)
            # 应用 Markdown 高亮
            current_theme = self.settings_manager.get_theme()
            highlighter_colors = theme.get_theme(current_theme)["highlighter"]
            self.highlighter = MarkdownHighlighter(self.editor.document(), theme_colors=highlighter_colors)

            # 连接 textChanged 信号到防抖方法
            self.editor.textChanged.connect(self.on_text_changed)

            right_splitter.addWidget(self.editor)

            # 预览区
            self.preview = QWebEngineView()
            self.preview.setContextMenuPolicy(Qt.NoContextMenu)  # 禁用右键菜单
            right_splitter.addWidget(self.preview)

            splitter.addWidget(right_splitter)
            splitter.setSizes([200, 1200])

            self.setCentralWidget(splitter)

            # 应用主题
            self.apply_theme(current_theme)

            # 初始预览更新
            self.update_preview()

        except Exception as e:
            QMessageBox.critical(self, "初始化错误", f"初始化界面时发生错误: {e}")

    def apply_theme(self, theme_name):
        """
        应用指定的主题。
        """
        try:
            theme_config = theme.get_theme(theme_name)
            if not theme_config:
                QMessageBox.warning(self, "警告", f"未知的主题名称: {theme_name}")
                return

            palette = QPalette()
            for role, color in theme_config["palette"].items():
                qcolor = QColor(color)
                if hasattr(QPalette, role):
                    palette.setColor(getattr(QPalette, role), qcolor)

            # 设置全局调色板
            QApplication.setPalette(palette)

            # 更新高亮器颜色
            self.highlighter.set_theme(theme_config["highlighter"])

            # 更新预览区以应用新的颜色
            self.update_preview()

        except Exception as e:
            QMessageBox.critical(self, "错误", f"应用主题时发生错误: {e}")

    def new_file(self):
        try:
            if self.maybe_save():
                # 弹出对话框让用户输入新文件名
                file_name, ok = QInputDialog.getText(self, "新建文件", "输入新文件名（不含扩展名）:")
                if ok and file_name:
                    # 确保文件名不为空
                    file_name = file_name.strip()
                    if file_name:
                        # 为文件名添加扩展名
                        file_name = f"{file_name}.md"

                        # 创建完整路径
                        if self.current_folder:
                            new_file_path = os.path.join(self.current_folder, file_name)
                        else:
                            # 如果没有当前文件夹，提示用户选择文件夹
                            self.open_folder()
                            if not self.current_folder:
                                return  # 如果用户没有选择文件夹，则取消新建操作
                            new_file_path = os.path.join(self.current_folder, file_name)

                        # 检查文件是否已存在
                        if os.path.exists(new_file_path):
                            QMessageBox.warning(self, "警告", f"文件 '{file_name}' 已存在，请选择其他名称。")
                            return

                        # 创建新文件并写入空内容
                        with open(new_file_path, 'w', encoding='utf-8') as f:
                            f.write("")

                        # 清空编辑区并设置新文件的路径
                        self.editor.clear()
                        self.current_file = new_file_path
                        self.setWindowTitle(f"Cmx的 Markdown 编辑器 - {os.path.basename(self.current_file)}")

                        # 将新文件添加到左侧文件列表
                        self.file_list.addItem(file_name)

                        # 自动选中左侧列表中新添加的文件项
                        items = self.file_list.findItems(file_name, Qt.MatchExactly)
                        if items:
                            item = items[0]
                            self.file_list.setCurrentItem(item)

                        # 更新预览区
                        self.update_preview()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"创建新文件时发生错误: {e}")

    def open_folder(self):
        try:
            folder = QFileDialog.getExistingDirectory(self, "选择文件夹", "")
            if folder:
                self.current_folder = folder
                self.populate_file_list(folder)
                # 保存上次打开的文件夹
                self.settings_manager.set_last_opened_folder(folder)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"打开文件夹时发生错误: {e}")

    def del_file(self):
        try:
            if self.current_file:
                reply = QMessageBox.question(self, "删除文件", f"确定要删除文件 '{os.path.basename(self.current_file)}' 吗？",
                                             QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if reply == QMessageBox.Yes:
                    os.remove(self.current_file)
                    self.current_file = None
                    self.editor.clear()
                    self.setWindowTitle("Cmx的 Markdown 编辑器")
                    self.populate_file_list(self.current_folder)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"删除文件时发生错误: {e}")

    def populate_file_list(self, folder):
        try:
            self.file_list.clear()
            for file_name in os.listdir(folder):
                if file_name.endswith('.md') or file_name.endswith('.markdown'):
                    self.file_list.addItem(file_name)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"列出文件时发生错误: {e}")

    def open_file(self):
        try:
            if self.maybe_save():
                options = QFileDialog.Options()
                file_name, _ = QFileDialog.getOpenFileName(
                    self, "打开 Markdown 文件", "",
                    "Markdown Files (*.md *.markdown);;All Files (*)", options=options)
                if file_name:
                    self.load_file(file_name)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"打开文件时发生错误: {e}")

    def load_file(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            self.editor.setPlainText(content)
            self.current_file = file_path
            self.setWindowTitle(f"Cmx的 Markdown 编辑器 - {os.path.basename(file_path)}")
            self.update_preview()  # 更新预览区
            # 保存上次打开的文件
            self.settings_manager.set_last_opened_file(file_path)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"无法打开文件: {e}")

    def load_selected_file(self, item):
        try:
            if self.maybe_save():
                file_path = os.path.join(self.current_folder, item.text())
                self.load_file(file_path)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载选定文件时发生错误: {e}")

    def save_file(self):
        try:
            if self.current_file:
                with open(self.current_file, 'w', encoding='utf-8') as f:
                    f.write(self.editor.toPlainText())
                self.editor.document().setModified(False)
                self.setWindowTitle(f"Cmx的 Markdown 编辑器 - {os.path.basename(self.current_file)}")
            else:
                self.save_file_as()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"无法保存文件: {e}")

    def save_file_as(self):
        try:
            options = QFileDialog.Options()
            file_name, _ = QFileDialog.getSaveFileName(
                self, "保存 Markdown 文件", "",
                "Markdown Files (*.md *.markdown);;All Files (*)", options=options)
            if file_name:
                with open(file_name, 'w', encoding='utf-8') as f:
                    f.write(self.editor.toPlainText())
                self.current_file = file_name
                self.setWindowTitle(f"Cmx的 Markdown 编辑器 - {os.path.basename(file_name)}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"无法保存文件: {e}")

    def maybe_save(self):
        try:
            if self.editor.document().isModified():
                ret = QMessageBox.warning(
                    self, "警告",
                    "文档已修改但未保存。是否保存？",
                    QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
                if ret == QMessageBox.Save:
                    self.save_file()
                    return True
                elif ret == QMessageBox.Cancel:
                    return False
            return True
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存检查时发生错误: {e}")
            return False

    def on_text_changed(self):
        # 每次文本变化时，重新启动防抖定时器
        self.preview_update_timer.start(300)  # 300毫秒后执行预览更新

    def update_preview(self):
        try:
            md_text = self.editor.toPlainText()
            html = markdown.markdown(
                md_text,
                extensions=['fenced_code', 'tables', 'codehilite'],
                extension_configs={
                    'codehilite': {
                        'noclasses': False,  # 使用类而不是行内样式
                        'guess_lang': False  # 禁止自动猜测语言
                    }
                }
            )
            # 生成 CSS 和引入 highlight.js
            css = self.generate_css()
            # 组合完整的 HTML
            full_html = f"<head>{css}</head><body>{html}</body>"

            # 设置 baseUrl 为当前文件所在目录
            if self.current_file:
                base_url = QUrl.fromLocalFile(os.path.dirname(self.current_file) + os.sep)
            else:
                base_url = QUrl()

            self.preview.setHtml(full_html, base_url)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"更新预览时发生错误: {e}")

    def generate_css(self):
        """
        生成当前编辑器和预览区的 CSS 样式
        """
        # 从全局调色板中提取背景色和文本色
        global_palette = QApplication.palette()
        bg_color = global_palette.color(QPalette.Window).name()
        text_color = global_palette.color(QPalette.WindowText).name()
        font = QApplication.font()
        font_family = font.family()
        font_size = font.pointSize()

        # 选择一个 highlight.js 主题，例如 GitHub
        highlight_css = """
        <link rel="stylesheet"
              href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.7.0/styles/github.min.css">
        """

        highlight_js = """
        <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.7.0/highlight.min.js"></script>
        <script>hljs.highlightAll();</script>
        """

        css = f"""
        <style>
            body {{
                background-color: {bg_color};
                color: {text_color};
                font-family: "{font_family}";
                font-size: {font_size}pt;
                padding: 20px;
            }}
            pre {{
                background-color: #f0f0f0;
                color: #333333;
                padding: 10px;
                border-radius: 5px;
                overflow: auto;
            }}
            code {{
                background-color: #f0f0f0;
                color: #333333;
                padding: 2px 4px;
                border-radius: 3px;
            }}
            table {{
                border-collapse: collapse;
            }}
            table, th, td {{
                border: 1px solid #555555;
            }}
            th, td {{
                padding: 8px;
                text-align: left;
            }}
            a {{
                color: #1e90ff;
            }}
        </style>
        {highlight_css}
        {highlight_js}
        """
        return css

    def init_auto_save(self):
        try:
            self.auto_save_timer = QTimer()
            self.auto_save_timer.timeout.connect(self.auto_save)
            self.auto_save_timer.start(30000)  # 每30秒自动保存
        except Exception as e:
            QMessageBox.critical(self, "错误", f"初始化自动保存时发生错误: {e}")

    def auto_save(self):
        try:
            if self.current_file and self.editor.document().isModified():
                with open(self.current_file, 'w', encoding='utf-8') as f:
                    f.write(self.editor.toPlainText())
                self.editor.document().setModified(False)
                self.setWindowTitle(f"Cmx的 Markdown 编辑器 - {os.path.basename(self.current_file)}")
                # 为了避免频繁弹出提示，注释掉以下行
                # QMessageBox.information(self, "自动保存", "文件已自动保存。")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"自动保存时发生错误: {e}")

    def open_settings(self):
        try:
            dialog = SettingsDialog(self)
            dialog.exec_()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"打开设置时发生错误: {e}")

    def make_bold(self):
        try:
            cursor = self.editor.textCursor()
            cursor.insertText("**加粗文本**")
            self.editor.setTextCursor(cursor)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"插入加粗文本时发生错误: {e}")

    def make_italic(self):
        try:
            cursor = self.editor.textCursor()
            cursor.insertText("*斜体文本*")
            self.editor.setTextCursor(cursor)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"插入斜体文本时发生错误: {e}")

    def make_heading(self):
        try:
            cursor = self.editor.textCursor()
            cursor.insertText("# 标题")
            self.editor.setTextCursor(cursor)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"插入标题时发生错误: {e}")

    def make_list(self):
        try:
            cursor = self.editor.textCursor()
            current_block = cursor.block().text()
            # 计算当前行的缩进级别
            indent_level = 0
            match = re.match(r'^(\s*)-', current_block)
            if match:
                indent_spaces = len(match.group(1))
                indent_level = indent_spaces // 4 + 1  # 每4个空格为一级

            # 构造缩进
            indent = '    ' * indent_level
            list_item = f"{indent}- 列表项\n"
            cursor.insertText(list_item)
            self.editor.setTextCursor(cursor)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"插入列表项时发生错误: {e}")

    def insert_image(self):
        try:
            options = QFileDialog.Options()
            image_path, _ = QFileDialog.getOpenFileName(
                self, "选择图片", "",
                "Image Files (*.png *.jpg *.jpeg *.bmp *.gif);;All Files (*)", options=options)
            if image_path:
                # 将图片复制到当前文件夹下的images目录
                if self.current_file:
                    images_dir = os.path.join(os.path.dirname(self.current_file), 'images')
                    os.makedirs(images_dir, exist_ok=True)
                    image_name = os.path.basename(image_path)
                    new_image_path = os.path.join(images_dir, image_name)
                    if not os.path.exists(new_image_path):
                        try:
                            shutil.copy(image_path, new_image_path)
                        except Exception as e:
                            QMessageBox.critical(self, "错误", f"无法复制图片: {e}")
                            return
                    relative_path = os.path.relpath(new_image_path, os.path.dirname(self.current_file))
                    cursor = self.editor.textCursor()
                    markdown_image = f"![图片]({relative_path})"
                    cursor.insertText(markdown_image)
                    self.editor.setTextCursor(cursor)
                    # 不需要在这里启动防抖定时器，因为 textChanged 已经处理
                else:
                    QMessageBox.warning(self, "警告", "请先保存文件后再插入图片。")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"插入图片时发生错误: {e}")

    def insert_code_block(self):
        try:
            # 定义可供选择的编程语言
            languages = [
                "python", "cpp", "java", "javascript", "csharp", "ruby",
                "go", "html", "css", "bash", "json", "xml", "php", "swift",
                "kotlin", "rust", "typescript"
            ]

            # 弹出输入对话框让用户选择语言
            lang, ok = QInputDialog.getItem(
                self, "选择编程语言", "编程语言:", languages, 0, False
            )

            if ok and lang:
                # 插入代码块语法
                cursor = self.editor.textCursor()
                code_block = f"```{lang}\n\n```\n"
                cursor.insertText(code_block)
                # 将光标移动到代码块内部
                cursor.movePosition(QTextCursor.PreviousBlock)
                cursor.movePosition(QTextCursor.EndOfBlock)
                self.editor.setTextCursor(cursor)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"插入代码块时发生错误: {e}")

def main():
    try:
        app = QApplication(sys.argv)
        app.setApplicationName("Cmx的 Markdown 编辑器")

        # 初始化设置管理器并应用设置
        settings_manager = SettingsManager()
        current_theme = settings_manager.get_theme()
        initial_font = settings_manager.get_font()
        app.setFont(initial_font)
        # 应用主题
        theme_config = theme.get_theme(current_theme)
        if theme_config:
            palette = QPalette()
            for role, color in theme_config["palette"].items():
                qcolor = QColor(color)
                if hasattr(QPalette, role):
                    palette.setColor(getattr(QPalette, role), qcolor)
            app.setPalette(palette)
        else:
            app.setPalette(app.palette())  # 默认调色板

        window = MarkdownEditor()
        window.show()
        sys.exit(app.exec_())
    except Exception as e:
        QMessageBox.critical(None, "致命错误", f"应用程序发生致命错误: {e}")

if __name__ == '__main__':
    main()


