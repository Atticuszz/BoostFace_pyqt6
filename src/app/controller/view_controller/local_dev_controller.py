# coding=utf-8
from PyQt6.QtGui import QTextCursor

from src.app.common import signalBus
from src.app.model.view_model.local_dev_model import LocalDevModel
from src.app.view.interface.local_dev_interface import LocalDevInterface


class LocalDevController:
    """
    connect console_append_text to update console log view
    """

    def __init__(self, model: LocalDevModel, view: LocalDevInterface):
        self.model = model
        self.view = view

        # self.model.console_simulator.newText.connect(self.console_append_text)
        # receive log message from all sender in the bus
        signalBus.log_message.connect(self.console_append_text)
        self.model.console_simulator.start()

    def console_append_text(self, text):
        """
        listen to the newText signal and append the text to the text edit
        :param text:
        :return:
        """
        cursor = self.view.console_log.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.insertText(text)
        self.view.console_log.setTextCursor(cursor)
