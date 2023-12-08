from PyQt6.QtCore import Qt
from qfluentwidgets import InfoBar, InfoBarPosition


class InforBarCreaterV:
    def __init__(self, parent):
        self.main_window = parent

    def login_failed(self, content: str):
        InfoBar.error(
            title='Login Failed',
            content=content,
            orient=Qt.Orientation.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            # position='Custom',   # NOTE: use custom info bar manager
            duration=-1,
            parent=self.main_window
        )

    def login_successfully(self, content: str):
        InfoBar.success(
            title='Login Successfully',
            content=content,
            orient=Qt.Orientation.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            # position='Custom',   # NOTE: use custom info bar manager
            duration=2000,
            parent=self.main_window
        )
