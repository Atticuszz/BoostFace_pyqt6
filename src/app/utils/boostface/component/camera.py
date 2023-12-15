"""
-*- coding: utf-8 -*-
@Organization : SupaVision
@Author       : 18317
@Date Created : 14/12/2023
@Description  :
    camera.py for boostface
"""
from enum import Enum
from typing import NamedTuple

import cv2
from time import sleep

from src.app.config import cfg
from src.app.config import qt_logger
from src.app.time_tracker import time_tracker
from src.app.utils.boostface.component.common import ImageFaces


class CameraOpenError(Exception):
    """
    CameraOpenError
    """

    def __init__(self, message):
        super().__init__(message)
        self.message = message


class CameraUrl(Enum):
    """
    url configs for camera
    """
    laptop: int = 0
    usb: int = 1
    ip: str = "http://"
    video: str = r"C:\Users\18317\OneDrive\python\BoostFace\src\boostface\db\data\test_01\video\Nola_Lyirs.mp4"


class CameraConfig(NamedTuple):
    """
    config for Camera
    """
    fps: int = 30
    resolution: tuple[int, ...] = (1920, 1080)
    url: CameraUrl = CameraUrl.usb


class Camera:
    """
    read image from camera by opencv.VideoCapture.read() from the given url
    """

    def __init__(
            self, config: CameraConfig = CameraConfig(
                fps=cfg.cameraFps.value)):
        """
        cmd 运行setx OPENCV_VIDEOIO_PRIORITY_MSMF 0后重启，可以加快摄像头打开的速度
        :param config: CameraOptions()
        """
        self.config = config
        self.videoCapture = cv2.VideoCapture(self.config.url.value)
        if config.url != CameraUrl.video:
            self._prepare()
        qt_logger.debug(f"camera init success, {self}")

    def read(self) -> ImageFaces:
        """
        read a Image from url by opencv.VideoCapture.read()
        :return: Image
        """
        with time_tracker.track("pure Camera.read"):
            ret, frame = self.videoCapture.read()
            if ret is None or frame is None:
                raise CameraOpenError(
                    f"in {self}.read()  self.videoCapture.read() get None")
            if self.config.url == CameraUrl.video:
                # sleep(1 / self.config.fps)
                sleep(0.005)
            elif self.config.url == CameraUrl.usb:
                sleep(0.0001)
            # logging.debug(f"camera read success{frame.shape}")
        return ImageFaces(image=frame, faces=[])

    def stop_device(self):
        """
        release camera
        """
        if self.videoCapture.isOpened():
            self.videoCapture.release()
            qt_logger.debug("camera release success")

    def __repr__(self):
        """
        print camera info
        """
        self.real_resolution = int(
            self.videoCapture.get(
                cv2.CAP_PROP_FRAME_WIDTH)), int(
            self.videoCapture.get(
                cv2.CAP_PROP_FRAME_HEIGHT))
        # 获取帧数
        self.real_fps = int(self.videoCapture.get(cv2.CAP_PROP_FPS))
        repr_string = (f"The video  codec  is {self.cap_codec_format}\n"
                       f"camera params = {self.config}")
        return repr_string

    def _prepare(self):
        """
        for usb or ip camera, set fps and resolution, not necessary for mp4
        :return:
        """
        #  设置帧数
        self.videoCapture.set(cv2.CAP_PROP_FPS, self.config.fps)
        # 设置分辨率
        self.videoCapture.set(
            cv2.CAP_PROP_FRAME_WIDTH,
            self.config.resolution[0])
        self.videoCapture.set(
            cv2.CAP_PROP_FRAME_HEIGHT,
            self.config.resolution[1])

        # 设置视频编解码格式 note: 务必在set分辨率之后设置，否则不知道为什么又会回到默认的YUY2
        self.videoCapture.set(
            cv2.CAP_PROP_FOURCC, cv2.VideoWriter.fourcc("M", "J", "P", "G")
        )

    @property
    def cap_codec_format(self):
        """
        get current video codec format
        :return:
        """
        # 获取当前的视频编解码器
        fourcc = self.videoCapture.get(cv2.CAP_PROP_FOURCC)
        # 因为FOURCC编码是一个32位的值，我们需要将它转换为字符来理解它
        # 将整数编码值转换为FOURCC编码的字符串表示形式
        codec_format = "".join(
            [chr((int(fourcc) >> 8 * i) & 0xFF) for i in range(4)])
        return codec_format


if __name__ == "__main__":
    camera = Camera()
    i = 0
    while i < 1000:
        img = camera.read()
        if cv2.waitKey(1) == 27:
            break
        i += 1
    camera.stop_device()
    cv2.destroyAllWindows()
    time_tracker.close()
