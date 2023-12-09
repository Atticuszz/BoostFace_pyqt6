import sys
from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QPixmap, QPainter, QPainterPath, QLinearGradient, QColor, QBrush
from PyQt6.QtWidgets import QApplication
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from qfluentwidgets import FluentIcon as FIF
from qfluentwidgets import TogglePushButton
from qfluentwidgets import isDarkTheme, FluentIcon

from src.app.config.config import HELP_URL, REPO_URL, EXAMPLE_URL, FEEDBACK_URL
from src.app.model.component_model.camera_model import CameraModel
from src.app.view.component.link_card import LinkCardView


class VideoStreamWidget(QWidget):
    """ Widget to display video stream from camera"""

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.img_size = (960, 540)
        self.default_pixmap = QPixmap(self.img_size[0], self.img_size[1])
        self.default_pixmap.fill(QColor(0, 0, 0, 0))
        self.image_label = QLabel(self)
        self.image_label.setPixmap(self.default_pixmap)

    def update_image(self, image):
        """start camera to update image"""
        scaled_image = QPixmap.fromImage(image).scaled(
            self.img_size[0],
            self.img_size[1],
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation)
        self.image_label.setPixmap(scaled_image)

    def reset_image(self):
        """reset image"""
        self.image_label.setPixmap(self.default_pixmap)


class CameraWidget(VideoStreamWidget):
    """
    camera_card
    |--- start button
    |---VideoStreamWidget

    add control components on video stream widget
    """

    def __init__(self, parent=None, model: CameraModel | None = None, ):
        super().__init__(parent=parent)
        self.model = model
        self.layout = QVBoxLayout(self)

        # need to connect in controller
        self.toggle_switch = TogglePushButton(
            FIF.PLAY_SOLID, "start camera", self)

        self.layout.addWidget(self.image_label)
        # self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.layout.addWidget(self.toggle_switch)
        # self.setLayout(self.layout)

    def closeEvent(self, event) -> None:
        self.model.stop()
        super().closeEvent(event)


class StateWidget(QWidget):
    """
    state_card
    |---background
    |---card CPU
    |---card RAM
    |---card Running time
    |---card connect to cloud
    """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setFixedHeight(200)

        self.vBoxLayout = QVBoxLayout(self)

        # label
        self.galleryLabel = QLabel('BoostFace System', self)

        # banner image
        self.banner = QPixmap(':/gallery/images/header1.png')

        self.linkCardView = LinkCardView(self)

        self.galleryLabel.setObjectName('galleryLabel')

        self.vBoxLayout.setSpacing(0)
        self.vBoxLayout.setContentsMargins(0, 20, 0, 0)
        self.vBoxLayout.addWidget(self.galleryLabel)
        self.vBoxLayout.addWidget(
            self.linkCardView, 1, Qt.AlignmentFlag.AlignBottom)
        self.vBoxLayout.setAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)

        self.linkCardView.addCard(
            ':/gallery/images/logo.png',
            self.tr('Getting started'),
            self.tr('An overview of app development options and samples.'),
            HELP_URL
        )

        self.linkCardView.addCard(
            FluentIcon.GITHUB,
            self.tr('GitHub repo'),
            self.tr(
                'The latest fluent design controls and styles for your applications.'),
            REPO_URL
        )

        self.linkCardView.addCard(
            FluentIcon.CODE,
            self.tr('Code samples'),
            self.tr(
                'Find samples that demonstrate specific tasks, features and APIs.'),
            EXAMPLE_URL
        )

        self.linkCardView.addCard(
            FluentIcon.FEEDBACK,
            self.tr('Send feedback'),
            self.tr('Help us improve PyQt-Fluent-Widgets by providing feedback.'),
            FEEDBACK_URL
        )

    def paintEvent(self, e):
        super().paintEvent(e)
        painter = QPainter(self)
        painter.setRenderHints(
            QPainter.RenderHint.SmoothPixmapTransform | QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)

        path = QPainterPath()
        path.setFillRule(Qt.FillRule.WindingFill)
        w, h = self.width(), self.height()
        path.addRoundedRect(QRectF(0, 0, w, h), 10, 10)
        path.addRect(QRectF(0, h - 50, 50, 50))
        path.addRect(QRectF(w - 50, 0, 50, 50))
        path.addRect(QRectF(w - 50, h - 50, 50, 50))
        path = path.simplified()

        # init linear gradient effect
        gradient = QLinearGradient(0, 0, 0, h)

        # draw background color
        if not isDarkTheme():
            gradient.setColorAt(0, QColor(207, 216, 228, 255))
            gradient.setColorAt(1, QColor(207, 216, 228, 0))
        else:
            gradient.setColorAt(0, QColor(0, 0, 0, 255))
            gradient.setColorAt(1, QColor(0, 0, 0, 0))

        painter.fillPath(path, QBrush(gradient))

        # draw banner image
        pixmap = self.banner.scaled(
            self.size(),
            Qt.AspectRatioMode.IgnoreAspectRatio,
            Qt.TransformationMode.SmoothTransformation)
        painter.fillPath(path, QBrush(pixmap))


class CameraView(QWidget):
    """
    state_widget
    camera_card
    """

    def __init__(self, model: CameraModel, parent=None):
        super().__init__(parent=parent)
        self.model = model
        self.vBoxLayout = QVBoxLayout(self)
        self.stateWidget = StateWidget(self)
        self.cameraCard = CameraWidget(self)
        self.vBoxLayout.addWidget(self.stateWidget)
        self.vBoxLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.vBoxLayout.addWidget(self.cameraCard)

    def closeEvent(self, event) -> None:
        self.model.stop()
        super().closeEvent(event)


if __name__ == '__main__':
    from src.app.controller.component_controller.camera_controller import CameraController
    from src.app.model.component_model.result_widget_model import ResultWidgetModel
    from src.app.view.component.result_widget import ResultsWidget
    from src.app.controller.component_controller.result_widget_contoller import ResultsController

    app = QApplication(sys.argv)
    model = CameraModel()
    view = CameraView(model)
    controller = CameraController(model, view)
    model2 = ResultWidgetModel()
    view2 = ResultsWidget(model2)
    controller2 = ResultsController(model2, view2)
    view.show()
    sys.exit(app.exec())
