# coding=utf-8
from PyQt6.QtGui import QTextCursor

from src.app.model.view_model.cloud_dev_model import CloudServerModel
from src.app.view.interface.cloud_dev_interface import CloudDevInterface


class CloudDevController:
    """
    connect console_append_text to update console log view
    """

    def __init__(self, model: CloudServerModel, view: CloudDevInterface):
        self.model = model
        self.view = view
        self.model.cloud_dev_data.connect(self.console_append_text)
        self.model.start()
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


if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    view = CloudDevInterface()
    model = CloudServerModel()
    controller = CloudDevController(model, view)
    view.show()
    sys.exit(app.exec())
