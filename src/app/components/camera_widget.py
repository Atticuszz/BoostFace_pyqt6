import sys

import cv2
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QImage
from PyQt6.QtGui import QPixmap, QPainter, QPainterPath, QLinearGradient, QColor, QBrush
from PyQt6.QtWidgets import QApplication
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from qfluentwidgets import FluentIcon as FIF
from qfluentwidgets import TogglePushButton
from qfluentwidgets import isDarkTheme, FluentIcon

from src.app.common.config import HELP_URL, REPO_URL, EXAMPLE_URL, FEEDBACK_URL
from src.app.components.link_card import LinkCardView
from src.app.plugin.camera import AiCamera, CameraOpenError
from src.app.plugin.detector.common import Image2Detect


class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(QImage)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._run_flag = False

    def run(self):
        self.capture = AiCamera()
        while self._run_flag:
            try:
                frame = self.capture.read()
            except CameraOpenError:
                print("camera open error or camera has released")
                break
            assert isinstance(frame, Image2Detect), "frame is not Image2Detect"
            rgb_image = cv2.cvtColor(frame.nd_arr, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            convert_to_Qt_format = QImage(
                rgb_image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
            self.change_pixmap_signal.emit(convert_to_Qt_format)

    def start_capture(self):
        self._run_flag = True
        if not self.isRunning():
            self.start()

    def stop_capture(self):
        self._run_flag = False
        if self.isRunning():
            self.capture.release()

    def stop(self):
        self.stop_capture()
        self.wait()


class VideoStreamWidget(QWidget):
    """ Widget to display video stream from camera"""

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.img_size = (960, 540)
        self.default_pixmap = QPixmap(self.img_size[0], self.img_size[1])
        self.default_pixmap.fill(QColor(0, 0, 0, 0))
        self.image_label = QLabel(self)
        self.image_label.setPixmap(self.default_pixmap)

        # 创建视频线程
        self.thread = VideoThread(self)
        self.thread.change_pixmap_signal.connect(self.update_image)

    def toggle_camera(self):
        """ toggle camera """
        if self.thread.isRunning():
            self.thread.stop_capture()
            # main thread has delay
            try:
                self.image_label.setPixmap(self.default_pixmap)
            except Exception as e:
                print(e)
        else:
            self.thread.start_capture()

    def update_image(self, image):
        """start camera to update image"""
        scaled_image = QPixmap.fromImage(image).scaled(
            self.img_size[0],
            self.img_size[1],
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation)
        self.image_label.setPixmap(scaled_image)

    def closeEvent(self, event):
        self.thread.stop()


class CameraWidget(VideoStreamWidget):
    """
    camera_card
    |--- start button
    |---VideoStreamWidget
    """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        # default picture
        self.toggle_switch = TogglePushButton(
            FIF.PLAY_SOLID, "start camera", self)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.image_label)
        # self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.layout.addWidget(self.toggle_switch)
        self.setLayout(self.layout)
        # listen to toggle switch
        self.toggle_switch.toggled.connect(self.toggle_camera)


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

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.vBoxLayout = QVBoxLayout(self)
        self.stateWidget = StateWidget(self)
        self.cameraCard = CameraWidget(self)
        self.vBoxLayout.addWidget(self.stateWidget)
        self.vBoxLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.vBoxLayout.addWidget(self.cameraCard)
        self.setLayout(self.vBoxLayout)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = CameraView()
    main_window.show()
    sys.exit(app.exec())
