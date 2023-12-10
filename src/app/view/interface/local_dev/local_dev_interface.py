import time
from PyQt6.QtCore import QThread
from PyQt6.QtGui import QTextCursor
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from qfluentwidgets import FluentIcon as FIF, TextEdit

from src.app.common import signalBus
from src.app.config import qt_logger
from src.app.config.logging_config import QLoggingHandler
from src.app.view.component.expand_info_card import ExpandInfoCard
from src.app.view.component.system_monitor import SystemMonitor, LocalSystemMonitorC, LoaclSystemStats

__all__ = ['create_local_dev_interface']


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
            qt_logger.info(f"Line {count}: The current count is {count}\n")


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


class LocalDevInterface(QWidget):
    """ Local development interface"""

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName('localDevInterface')
        # init layout
        self.main_layout = QHBoxLayout(self)
        self.bc_layout = QVBoxLayout()
        self.a_layout = QVBoxLayout()
        self.main_layout.addLayout(self.a_layout, 2)  # 加入主布局，比例为1
        self.main_layout.addLayout(self.bc_layout, 1)  # 加入主布局，比例为1

        # init widgets

        self._init_camera_card()
        self._init_resource_monitor()
        self._init_console_log()

        # add widgets to layout

        self.bc_layout.addWidget(self.camera_info_card, 1)
        self.bc_layout.addWidget(self.resource_monitor, 2)

        # init window
        self.setWindowTitle('Local Development Interface')
        self.resize(1000, 800)

    def _init_camera_card(self):
        # B区域：摄像头信息，这里假设您的ExpandInfoCard已经创建好了
        self.camera_info_card = ExpandInfoCard(
            FIF.CAMERA,
            self.tr('Camera Info'),
            parent=self
        )
        self.camera_info_card.add_info(
            {
                'Device name': 'USB2.0 Camera',
                'Connection type': 'USB',
                'Image resolution': '1920x1080',
                'Capture FPS': '30',
            }
        )

    def _init_resource_monitor(self):
        # C区域：资源监测图表
        sys_monitor_model = LoaclSystemStats()
        self.resource_monitor = SystemMonitor(self)
        self.resource_monitor_controller = LocalSystemMonitorC(
            self.resource_monitor, sys_monitor_model)

    def _init_console_log(self):
        """
        init console log
        :return:
        """
        # A区域：控制台日志输出
        self.console_log = TextEdit()
        self.console_log.setReadOnly(True)
        self.a_layout.addWidget(self.console_log)

    def append_text(self, text):
        """
        listen to the newText signal and append the text to the text edit
        :param text:
        :return:
        """
        cursor = self.console_log.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.insertText(text)
        self.console_log.setTextCursor(cursor)


class LocalDevC:
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


# TODO:separate the interface to several parts,Interface should be a class that only contains the layout and widgets


def create_local_dev_interface(parent=None) -> LocalDevC:
    """
    create local dev interface
    :param parent:
    :return:
    """
    created_model = LocalDevModel()
    created_view = LocalDevInterface(parent=parent)
    created_controller = LocalDevC(created_model, created_view)
    return created_controller


if __name__ == '__main__':
    from PyQt6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    view = LocalDevInterface()
    model = LocalDevModel()
    controller = LocalDevC(model, view)
    logging_header_set_up = QLoggingHandler()
    view.show()
    sys.exit(app.exec())
