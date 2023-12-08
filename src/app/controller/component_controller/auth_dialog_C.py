# coding=utf-8
import sys

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QWidget, QHBoxLayout
from qfluentwidgets import PushButton

from src.app.common import signalBus
from src.app.controller.component_controller.info_bar_C import InforBarCreaterC
from src.app.model.component_model.auth_dialog_M import AuthDialogM
from src.app.view.component.auth_dialog_V import AuthDialog
from src.app.view.component.info_bar_V import InforBarCreaterV


class AuthDialogC:
    def __init__(self, model: AuthDialogM, view: AuthDialog):
        self.model = model
        self.view = view

        # connect
        self.view.password_line_edit.textChanged.connect(
            self.model.set_password)
        self.view.email_line_edit.textChanged.connect(self.model.set_email)
        self.view.yesButton.clicked.connect(self.login)

    def login(self):
        if not self.model.validate_email():
            signalBus.login_failed.emit("your email is invalid!")
        elif not self.model.validate_password():
            signalBus.login_failed.emit("your password must have one uppercase letter,\
                                         one lowercase letter, one number, and one symbol At least 8, at most 16 characters ")
        elif not self.model.login():
            signalBus.login_failed.emit("login failed!")
        else:
            signalBus.login_successfully.emit("login successfully!")


class Demo(QWidget):

    def __init__(self):
        super().__init__()
        # setTheme(Theme.DARK)
        # self.setStyleSheet('Demo{background:rgb(32,32,32)}')

        self.hBxoLayout = QHBoxLayout(self)
        self.button = PushButton('打开 URL', self)

        self.resize(600, 600)
        self.hBxoLayout.addWidget(self.button, 0, Qt.AlignmentFlag.AlignCenter)
        self.button.clicked.connect(self.showDialog)

        self.info_bar = InforBarCreaterV(self)
        self.info_bar_c = InforBarCreaterC(self.info_bar)

    def showDialog(self):
        w = AuthDialog(self)
        model = AuthDialogM()
        controller = AuthDialogC(model, w)
        if w.exec():
            print(w.email_line_edit.text())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = Demo()
    w.show()
    app.exec()
