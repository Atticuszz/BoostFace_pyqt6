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
from src.app.types import Image
from src.app.utils.boostface.component.common import Image2Detect, WorkingThread


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
    url: CameraUrl = CameraUrl.laptop


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
        self.videoCapture = None
        self._open()
        if config.url != CameraUrl.video:
            self._prepare()
        qt_logger.debug(f"camera init success, {self}")

    def read(self) -> Image:
        """
        read a Image from url by opencv.VideoCapture.read()
        :return: Image
        """
        ret, frame = self.videoCapture.read()
        if ret is None or frame is None:
            qt_logger.warn("camera read failed")
            raise CameraOpenError(
                f"in {self}.read()  self.videoCapture.read() get None")
        return frame

    def release(self):
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

    def _open(self):
        """
        connect to camera  by url, raise ValueError if failed
        :return:
        """
        self.videoCapture = cv2.VideoCapture(self.config.url.value)
        if not self.videoCapture.isOpened():
            qt_logger.warn("camera open failed")
            raise CameraOpenError(
                f"Could not open video source from url: {self.config.url.value}")
        qt_logger.debug("camera open success")

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


class CameraWorker(Camera, WorkingThread):
    """
    generate Image2Detect into results queue from Camera instance may be in a thread
    """

    def __init__(self):
        super().__init__(works_name="camera_read", is_consumer=False)

    def produce(self) -> Image2Detect:
        """
        read image from camera
        """
        frame: Image = self.read()
        if self.config.url == CameraUrl.video:
            sleep(1 / self.config.fps)
            # print("camera_read get img")
        return Image2Detect(image=frame, faces=[])

    def stop_thread(self):
        self.release()
        super().stop_thread()
