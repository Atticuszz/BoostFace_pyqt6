# coding=utf-8

import cv2
import sys
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout

from src.app.plugin.camera import AiCamera


class VideoStreamWidget(QWidget):
    def __init__(self):
        super().__init__()

        # 初始化摄像头
        self.capture = AiCamera()

        # 创建一个 QLabel 来显示图像
        self.image_label = QLabel(self)
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.image_label)
        self.setLayout(self.layout)

        # 创建 QTimer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

    def update_frame(self):
        frame = self.capture.read()

        # 将图像从 BGR 转换为 RGB
        rgb_image = cv2.cvtColor(frame.nd_arr, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        p = convert_to_Qt_format.scaled(1920 // 2, 1080 // 2, Qt.AspectRatioMode.KeepAspectRatio)
        self.image_label.setPixmap(QPixmap.fromImage(p))

    def closeEvent(self, event):
        self.capture.release()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = VideoStreamWidget()
    main_window.show()
    sys.exit(app.exec())
