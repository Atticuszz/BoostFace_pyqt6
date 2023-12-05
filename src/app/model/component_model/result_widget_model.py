# coding=utf-8
import random

from PyQt6.QtCore import QThread, pyqtSignal


class RsultWidgetModel(QThread):
    newData = pyqtSignal(list)  # Signal to emit new data

    def __init__(self):
        super().__init__()
        self.column_count = 4
        self.headers = ['ID', 'Name', 'gender', 'Time']
        self._is_running = False

    def run(self):
        self._is_running = True
        while self._is_running:
            self.sleep(1)  # Wait for 1 second
            data = [
                str(
                    random.randint(
                        1, 100)), "Name {}".format(
                    random.randint(
                        1, 100)), "gender {}".format(
                    random.randint(
                        1, 100)), "Time {}".format(
                    random.randint(
                        1, 100))]
            self.newData.emit(data)  # Emit the signal with new data

    def stop(self):
        self._is_running = False
        self.wait()
