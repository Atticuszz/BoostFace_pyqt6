# coding=utf-8
import time

from PyQt6.QtCore import pyqtSignal, QThread


class ConsoleSimulator(QThread):
    """
    A console output simulator
    Signal: newText
    """
    newText = pyqtSignal(str)

    def run(self):
        count = 0
        while True:
            time.sleep(1)  # 控制输出速度
            count += 1
            self.newText.emit(f"Line {count}: The current count is {count}\n")


class CloudServerModel:
    """
    :var server_info: dict, server information
    :var console_simulator: ConsoleSimulator, a console output simulator
    """

    def __init__(self):
        self.server_info = {
            'domain': "www.digitalocean.com",
            'location': 'New York',
            'OS': 'Ubuntu 20.04',
            'CPU': '4 vCPU',
            'RAM': '8 GB',
            'GPU': 'NVIDIA RTX 3080',
            'Storage': '1 TB',
        }
        self.console_simulator = ConsoleSimulator()
