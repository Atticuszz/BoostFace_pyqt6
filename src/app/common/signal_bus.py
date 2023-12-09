# coding: utf-8
from PyQt6.QtCore import QObject, pyqtSignal


class SignalBus(QObject):
    """ pyqtSignal bus """

    switchToSampleCard = pyqtSignal(str, int)
    micaEnableChanged = pyqtSignal(bool)
    supportSignal = pyqtSignal()
    login_failed = pyqtSignal(str)
    login_successfully = pyqtSignal(str)
    is_identify_running = pyqtSignal(bool)
    log_message = pyqtSignal(str)


signalBus = SignalBus()
