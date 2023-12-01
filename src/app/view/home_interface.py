# coding:utf-8
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from qfluentwidgets import ScrollArea

from ..common.style_sheet import StyleSheet
from ..components.camera_widget import CameraView
from ..components.result_widget import ResultsWidget


class HomeInterface(ScrollArea):
    """ Home interface """

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        # 左侧布局 摄像头
        self.leftContainer = CameraView(self)
        self.leftVBox = QVBoxLayout(self.leftContainer)
        # 右边布局 结果列表
        self.rightContainer = ResultsWidget(self)
        self.rightVBox = QVBoxLayout(self.rightContainer)

        self.hBoxLayout = QHBoxLayout()
        self.hBoxLayout.addWidget(self.leftContainer, 2)  # 左侧比例为2
        self.hBoxLayout.addWidget(self.rightContainer, 1)  # 右侧比例为1

        self.view = QWidget(self)
        self.vBoxLayout = QVBoxLayout(self.view)

        self._init_left()
        self._init__right()
        self._init_view()

    def _init_left(self):
        self.leftContainer.setObjectName('leftContainer')
        self.leftVBox.setContentsMargins(0, 0, 0, 0)
        self.leftVBox.setSpacing(0)
        self.leftVBox.setAlignment(Qt.AlignmentFlag.AlignTop)

    def _init__right(self):
        self.rightContainer.setObjectName('rightContainer')
        self.rightVBox.setContentsMargins(0, 0, 0, 0)
        self.rightVBox.setSpacing(0)
        self.rightVBox.setAlignment(Qt.AlignmentFlag.AlignTop)

    def _init_view(self):
        self.view.setObjectName('view')
        self.setObjectName('homeInterface')

        # 将水平布局 hBoxLayout 设置为 view 的布局
        self.vBoxLayout.addLayout(self.hBoxLayout)

        StyleSheet.HOME_INTERFACE.apply(self)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setWidget(self.view)
        self.setWidgetResizable(True)
