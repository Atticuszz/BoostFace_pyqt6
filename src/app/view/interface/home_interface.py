# coding:utf-8
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout

from src.app.model.component_model.camera_model import CameraModel
from src.app.view.component.camera_widget import CameraWidget, StateWidget


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
        init left widgets
        """
        # 创建相应的widget实例并添加到布局中
        self.camera_widget = CameraWidget()
        self.state_widget = StateWidget()

        self.left_A_layout.addWidget(self.state_widget)
        self.left_B_layout.addWidget(self.camera_widget)

    def _init_right_widgets(self):
        """
        init right widgets
        """
        self.result_widget = ResultsWidget()
        self.right_layout.addWidget(self.result_widget)


if __name__ == '__main__':
    import sys
    from PyQt6.QtWidgets import QApplication
    from src.app.controller.component_controller.camera_controller import CameraController
    from src.app.model.component_model.result_widget_model import ResultWidgetModel
    from src.app.view.component.result_widget import ResultsWidget
    from src.app.controller.component_controller.result_widget_contoller import ResultsController

    app = QApplication(sys.argv)
    model = CameraModel()
    view = CameraWidget(model=model)
    controller = CameraController(model, view)
    model2 = ResultWidgetModel()
    view2 = ResultsWidget(model2)
    controller2 = ResultsController(model2, view2)
    HomeInterface().show()
    sys.exit(app.exec())