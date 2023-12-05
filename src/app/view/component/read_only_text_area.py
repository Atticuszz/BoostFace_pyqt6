# coding=utf-8
from qfluentwidgets import TextEdit


class ReadOnlyTextArea(TextEdit):
    """ Text edit """

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        # Set the text edit to read-only
        self.setReadOnly(True)

    def contextMenuEvent(self, e):
        # Disable context menu
        pass

    def mousePressEvent(self, e):
        # Override to do nothing
        pass

    def mouseMoveEvent(self, e):
        # Override to do nothing
        pass

    def mouseReleaseEvent(self, e):
        # Override to do nothing
        pass

    def keyPressEvent(self, e):
        # Override to do nothing and avoid any keyboard input
        pass


if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    w = ReadOnlyTextArea()
    w.show()
    sys.exit(app.exec())
