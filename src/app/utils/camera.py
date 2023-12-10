# coding=utf-8
"""
加速摄像头启动
cmd 运行setx OPENCV_VIDEOIO_PRIORITY_MSMF 0后重启，可以加快摄像头打开的速度
"""
import random
from enum import Enum
from typing import NamedTuple

import cv2

from .detector.common import Image, Image2Detect, Bbox, Color

__all__ = ["AiCamera"]

from .detector import Detector
from src.app.config.config import cfg


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

    def __init__(self, config: CameraConfig = CameraConfig(fps=cfg.cameraFps.value)):
        """
        cmd 运行setx OPENCV_VIDEOIO_PRIORITY_MSMF 0后重启，可以加快摄像头打开的速度
        :param config: CameraOptions()
        """
        self.config = config
        self.videoCapture = None
        self._open()
        if config.url != CameraUrl.video:
            self._prepare()
        print(self)

    def read(self) -> Image:
        """
        read a Image from url by opencv.VideoCapture.read()
        :return: Image
        """
        ret, frame = self.videoCapture.read()
        if ret is None or frame is None:
            raise CameraOpenError(
                f"in {self}.read()  self.videoCapture.read() get None")
        return frame

    def release(self):
        """
        release camera
        """
        if self.videoCapture.isOpened():
            self.videoCapture.release()

    def __repr__(self):
        """
        print camera info
        :return:
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
            raise CameraOpenError(
                f"Could not open video source from url: {self.config.url.value}")

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


class AiCamera(Camera):
    """
    get image from camera and run ai model get result
    """

    def __init__(self, config: CameraConfig = CameraConfig()):
        super().__init__(config)
        self._detector = Detector()
        self._colors: list[Color] = [
            (200, 150, 255), (255, 255, 153), (144, 238, 144), (173, 216, 230), (255, 182, 193), (255, 165, 0)]

    def read(self) -> Image2Detect:
        """
        read a Image from url by opencv.VideoCapture.read()
        :return: Image
        """
        frame = super().read()
        img2detect = Image2Detect(frame, [])
        img2detect = self._detector.run_onnx(img2detect)
        for face in img2detect.faces:
            self._draw_bbox(img2detect.nd_arr, face.bbox)
        return img2detect

    def _draw_bbox(self, dimg: Image, bbox: Bbox):
        """
        only draw the bbox beside the corner,and the corner is round
        :param dimg: img to draw bbox on
        :param bbox: face bboxes
        """
        # 定义矩形的四个角的坐标
        bbox = bbox.astype(int)
        pt1 = (bbox[0], bbox[1])
        pt2 = (bbox[2], bbox[3])
        bbox_thickness = 4
        # 定义直角附近线段的长度
        line_len = int(0.08 * (pt2[0] - pt1[0]) + 0.06 * (pt2[1] - pt1[1]))

        bbox_color = random.choice(self._colors)

        def draw_line(_pt1, _pt2):
            cv2.line(dimg, _pt1, _pt2, bbox_color, bbox_thickness)

        draw_line((pt1[0], pt1[1]), (pt1[0] + line_len, pt1[1]))
        draw_line((pt1[0], pt1[1]), (pt1[0], pt1[1] + line_len))
        draw_line((pt2[0], pt1[1]), (pt2[0] - line_len, pt1[1]))
        draw_line((pt2[0], pt1[1]), (pt2[0], pt1[1] + line_len))
        draw_line((pt1[0], pt2[1]), (pt1[0] + line_len, pt2[1]))
        draw_line((pt1[0], pt2[1]), (pt1[0], pt2[1] - line_len))
        draw_line((pt2[0], pt2[1]), (pt2[0] - line_len, pt2[1]))
        draw_line((pt2[0], pt2[1]), (pt2[0], pt2[1] - line_len))
