from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from qfluentwidgets import FluentIcon as FIF, TextEdit

from src.app.view.component.expand_info_card import ExpandInfoCard
from src.app.view.component.system_monitor import SystemMonitor


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
        self.resource_monitor = SystemMonitor(self)

    def _init_console_log(self):
        """
        init console log
        :return:
        """
        # A区域：控制台日志输出
        self.console_log = TextEdit()
        self.console_log.setReadOnly(True)
        self.a_layout.addWidget(self.console_log)
