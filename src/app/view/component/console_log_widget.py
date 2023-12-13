# coding=utf-8
from typing import Callable, Union

from PyQt6.QtGui import QTextCursor
from qfluentwidgets import TextEdit


class ConsoleLogWidget(TextEdit):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        # Readonly
        self.setReadOnly(True)
        self.close_event: Union[Callable, None] = None

    def append_text(self, text: str):
        """
        listen to the newText signal and append the text to the text edit
        :param text:
        """
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.insertText(text)
        self.setTextCursor(cursor)

    def closeEvent(self, event):
        """
        close event for thread
        :param event:
        """
        if self.close_event:
            self.close_event()
        super().closeEvent(event)
