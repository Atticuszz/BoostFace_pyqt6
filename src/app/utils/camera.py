# coding=utf-8
import random
from typing import Generator

import cv2

from .boostface.component.common import ImageFaces
from .boostface.main import BoostFace

__all__ = ["AiCamera"]

from ..time_tracker import time_tracker

from ..types import Color, Image, Bbox


class AiCamera(BoostFace):
    """
    get image from camera and run ai model get result
    """

    def __init__(self):
        super().__init__()
        self._colors: list[Color] = [(200, 150, 255), (255, 255, 153), (
            144, 238, 144), (173, 216, 230), (255, 182, 193), (255, 165, 0)]
        self._image_queue = self.image_queue()
        self.start()

    def read(self) -> Generator[ImageFaces, None, None]:
        """
        read a Image from url by opencv.VideoCapture.read()
        :return: Image
        """
        with time_tracker.track("AiCamera.read"):
            for image in self._image_queue:
                for face in image.faces:
                    self._draw_bbox(image.nd_arr, face.bbox)
                yield image

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
