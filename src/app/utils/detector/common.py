# coding=utf-8
from typing import NamedTuple

import numpy as np
from numpy._typing import NDArray

Kps = NDArray[np.float64]  # shape: (5, 2)
Bbox = NDArray[np.float64]  # shape: (4, 2)
Embedding = NDArray[np.float64]  # shape: (512, )
Image = NDArray[np.uint8]  # shape: (height, width, 3)
Color = tuple[int, int, int]


class Face2Search(NamedTuple):
    """
    face to search, it is a image filled with face for sending to search
    """
    face_img: Image
    bbox: Bbox
    kps: Kps
    det_score: float


class Face:
    def __init__(
            self,
            bbox: Bbox,
            kps: Kps,
            det_score: float,
            scene_scale: tuple[int, int, int, int],
            face_id: int = 0,
            color: Color = (50, 205, 255),
    ):
        """
        init a face
        :param bbox:shape [4,2]
        :param kps: shape [5,2]
        :param det_score:
        :param color:
        :param scene_scale: (x1,y1,x2,y2) of scense image
        :param match_info: MatchInfo(uid,score)
        """
        self.bbox: Bbox = bbox
        self.kps: Kps = kps
        self.det_score: float = det_score
        self.scense_scale: tuple[int, int, int, int] = scene_scale
        # 默认是橙色
        self.bbox_color: Color = color
        self.embedding: Embedding = np.zeros(512)
        self.id: int = face_id  # target id

    def face_image(self, scense: Image) -> Face2Search:
        """
        get face image from scense
        :param scense:
        :return:
        """
        # 确保 bbox 中的值是整数
        x1, y1, x2, y2 = map(
            int, [self.bbox[0], self.bbox[1], self.bbox[2], self.bbox[3]])

        # 避免超出图像边界
        x1 = max(0, x1)
        y1 = max(0, y1)
        x2 = min(scense.shape[1], x2)  # scense.shape[1] 是图像的宽度
        y2 = min(scense.shape[0], y2)  # scense.shape[0] 是图像的高度

        # 裁剪人脸图像
        face_img = scense[y1:y2, x1:x2]
        bbox = np.array([0, 0, face_img.shape[1], face_img.shape[0]])

        # 调整关键点位置
        kps = self.kps - np.array([x1, y1])

        return Face2Search(face_img, bbox, kps, self.det_score)


class Image2Detect:
    """
    image to detect
    :param image: image
    :param faces: [face, face, ...]
    """

    def __init__(self, image: Image, faces: list[Face]):
        self.nd_arr: Image = image
        self.faces: list[Face] = faces

    @property
    def scale(self) -> tuple[int, int, int, int]:
        """
        :return: (x1, y1, x2, y2)
        """
        return 0, 0, self.nd_arr.shape[1], self.nd_arr.shape[0]
