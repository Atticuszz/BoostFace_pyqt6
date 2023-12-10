from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QTextCursor
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from qfluentwidgets import FluentIcon as FIF, TextEdit

from src.app.common.client import WebSocketThread
from src.app.types import Image
from src.app.view.component.expand_info_card import ExpandInfoCard
from src.app.view.component.system_monitor import SystemMonitor
from src.app.view.interface.cloud_dev.remote_sm_widget import RemoteSystemStats, RemoteSystemMonitorC


# model


class CloudServerM(WebSocketThread):
    """
    :var server_info: dict, server information
    """
    cloud_dev_data = pyqtSignal(str)  # Signal to emit new data

    def __init__(self):
        super().__init__(ws_type="cloud_logging")
        self.server_info = {
            'domain': "www.digitalocean.com",
            'location': 'New York',
            'OS': 'Ubuntu 20.04',
            'CPU': '4 vCPU',
            'RAM': '8 GB',
            'GPU': 'NVIDIA RTX 3080',
            'Storage': '1 TB',
        }

    def working(self, data: dict | str | Image):
        if not isinstance(data, str):
            raise TypeError("data must be str")
        self.cloud_dev_data.emit(data)


# view


class CloudDevInterface(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName('CloudDevInterface')
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

        self.bc_layout.addWidget(self.cloud_info_card, 1)
        self.bc_layout.addWidget(self.resource_monitor, 2)

        # init window
        self.setWindowTitle('Local Development Interface')
        self.resize(1000, 800)

    def _init_camera_card(self):
        # B区域：摄像头信息，这里假设您的ExpandInfoCard已经创建好了
        self.cloud_info_card = ExpandInfoCard(
            FIF.GLOBE,
            self.tr('Cloud Server Info'),
            parent=self
        )

    def _init_resource_monitor(self):
        # C区域：资源监测图表
        model = RemoteSystemStats()
        self.resource_monitor = SystemMonitor(self)
        self.resource_monitor_controller = RemoteSystemMonitorC(
            self.resource_monitor, model)

    def _init_console_log(self):
        """
        init console log
        :return:
        """
        # A区域：控制台日志输出
        self.console_log = TextEdit()
        self.console_log.setReadOnly(True)
        self.a_layout.addWidget(self.console_log)


# controller
class CloudDevC:
    """
    connect console_append_text to update console log view
    """

    def __init__(self, model: CloudServerM, view: CloudDevInterface):
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


# TODO: separate into smaller components


def create_cloud_dev_interface(parent=None) -> CloudDevC:
    """
    create cloud dev interface
    :param parent:
    :return:
    """
    created_model = CloudServerM()
    created_view = CloudDevInterface(parent=parent)
    created_controller = CloudDevC(created_model, created_view)
    return created_controller
