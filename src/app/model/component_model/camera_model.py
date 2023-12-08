# coding=utf-8
# 在 model.py 文件中
import cv2
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtGui import QImage

from src.app.plugin.camera import AiCamera, CameraOpenError
from src.app.plugin.detector.common import Image2Detect


class CameraModel(QThread):
    """ Camera model """
    change_pixmap_signal = pyqtSignal(QImage)

    def __init__(self):
        super().__init__()
        self.capture = None
        self._is_running = False

    def run(self):
        self.capture = AiCamera()
        while self._is_running:
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
        # 启动摄像头和视频线程
        if not self.isRunning():
            self._is_running = True
            self.start()

    def stop_capture(self):
        # 停止摄像头和视频线程
        if self.isRunning():
            self._is_running = False
            self.wait()

    def stop(self):
        self._is_running = False
        self.wait()
        self.capture.release()
