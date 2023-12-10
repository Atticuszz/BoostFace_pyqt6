# coding:utf-8
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout

from src.app.view.interface.home.camera_widget import (
    create_camera_widget,
    create_state_widget)
from src.app.view.interface.home.result_widget import create_result_widget

__all__ = ['HomeInterface']


class HomeInterface(QWidget):
    """ Home interface """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName('homeInterface')

        self._init_layout()
        self._init_left_widgets()
        self._init_right_widgets()  # 方法名更改为更明确和一致

    def _init_layout(self):
        """
        init layout
        """
        self.main_layout = QHBoxLayout(self)  # 主布局
        self.left_layout = QVBoxLayout()  # 左侧布局
        self.left_A_layout = QVBoxLayout()  # 左A布局
        self.left_B_layout = QVBoxLayout()  # 左B布局
        self.right_layout = QVBoxLayout()  # 右侧布局

        # in left, A:B = 1:2
        self.left_layout.addLayout(self.left_A_layout, 1)
        self.left_layout.addLayout(self.left_B_layout, 2)

        # left:right = 2:1
        self.main_layout.addLayout(self.left_layout, 2)
        self.main_layout.addLayout(self.right_layout, 1)

    def _init_left_widgets(self):
        """
        init left widgets camera and state
        """
        self.camera_widget_C = create_camera_widget(self)
        self.camera_widget = self.camera_widget_C.view
        self.state_widget_C = create_state_widget(self)
        self.state_widget = self.state_widget_C.view

        self.left_A_layout.addWidget(self.state_widget)
        self.left_B_layout.addWidget(self.camera_widget)

    def _init_right_widgets(self):
        """
        init right widgets
        """
        self.result_widget_C = create_result_widget(self)
        self.result_widget = self.result_widget_C.view
        self.right_layout.addWidget(self.result_widget)


if __name__ == '__main__':
    pass
