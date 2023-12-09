# coding=utf-8
import logging

import time
from PyQt6.QtCore import QThread

from src.app.common import signalBus


class ConsoleSimulator(QThread):
    """
    A console output simulator
    Signal: newText
    """

    def run(self):
        count = 0
        while True:
            time.sleep(1)  # 控制输出速度
            count += 1
            logging.info(f"Line {count}: The current count is {count}\n")


class QLoggingHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        log_format = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s")
        self.setFormatter(log_format)
        logger = logging.getLogger()
        logger.addHandler(self)
        logger.setLevel(logging.INFO)

    def emit(self, record):
        log_entry = self.format(record)
        # auto send log message to the bus
        signalBus.log_message.emit(log_entry)


class LocalDevModel:
    """
    :var camera_info: dict, camera information
    :var console_simulator: ConsoleSimulator, a console output simulator
    """

    def __init__(self):
        self.console_simulator = ConsoleSimulator()
        self.camera_info = {
            'camera_name': 'Camera 1',
            'camera_type': 'USB',
            'camera_model': 'Logitech C920',
            'camera_resolution': '1920x1080',
            'camera_fps': '30',
            'camera_status': 'Connected',
        }
