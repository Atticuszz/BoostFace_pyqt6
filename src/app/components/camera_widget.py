import sys
from pathlib import Path

import cv2
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
from qfluentwidgets import FluentIcon as FIF
from qfluentwidgets import TogglePushButton

from src.app.plugin.camera import AiCamera


class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(QImage)

    def __init__(self):
        super().__init__()
        self._run_flag = False
        self._height = 480
        self._width = 960

    def run(self):
        self.capture = AiCamera()
        while self._run_flag:
            frame = self.capture.read()
            rgb_image = cv2.cvtColor(frame.nd_arr, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            convert_to_Qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
            p = convert_to_Qt_format.scaled(self._width, self._height, Qt.AspectRatioMode.KeepAspectRatio)
            self.change_pixmap_signal.emit(p)

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
    def __init__(self):
        super().__init__()

        bg_path: Path = Path(__file__).parents[1] / "resource" / "images" / "placeholder.png"
        self._video_bg = QPixmap(str(bg_path)).scaled(960, 440, Qt.AspectRatioMode.KeepAspectRatio,
                                                      Qt.TransformationMode.SmoothTransformation)
        # 图像亚力克

        # 创建一个 QLabel 来显示图像
        self.image_label = QLabel(self)
        self.image_label.setPixmap(self._video_bg)  # 显示初始图像

        self.toggle_switch = TogglePushButton(FIF.PLAY_SOLID, "start camera", self)
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.image_label)
        self.layout.addWidget(self.toggle_switch)
        self.setLayout(self.layout)

        # 创建视频线程
        self.thread = VideoThread()
        self.thread.change_pixmap_signal.connect(self.update_image)

        # 连接 toggle switch 的信号
        self.toggle_switch.toggled.connect(self.toggle_camera)

    def toggle_camera(self, checked):
        if checked:
            self.thread.start_capture()
        else:
            self.thread.stop_capture()
            self.image_label.setPixmap(self._video_bg)  # 显示初始图像

    def update_image(self, image):
        self.image_label.setPixmap(QPixmap.fromImage(image))

    def closeEvent(self, event):
        self.thread.stop()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = VideoStreamWidget()
    main_window.show()
    sys.exit(app.exec())
