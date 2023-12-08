# coding=utf-8
from src.app.common import signalBus
from src.app.view.component.info_bar_V import InforBarCreaterV


class InforBarCreaterC:
    def __init__(self, view: InforBarCreaterV):
        self.view = view
        self.auth_state_connect()

    def auth_state_connect(self):
        signalBus.login_failed.connect(self.view.login_failed)
        signalBus.login_successfully.connect(self.view.login_successfully)
