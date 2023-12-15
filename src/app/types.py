import base64
from typing import NamedTuple

import numpy as np
from numpy._typing import NDArray
from pydantic import BaseModel, Field

Kps = NDArray[np.float64]  # shape: (5, 2)
Bbox = NDArray[np.float64]  # shape: (4, 2)
Embedding = NDArray[np.float64]  # shape: (512, )
Image = NDArray[np.uint8]  # shape: (height, width, 3)
Color = tuple[int, int, int]


class MatchInfo(NamedTuple):
    score: float
    uid: str


# 定义 Pydantic 模型
class Face2SearchSchema(BaseModel):
    face_img: str = Field(..., description="Base64 encoded image data")
    bbox: list[float] = Field(...,
                              description="Bounding box coordinates")
    kps: list[list[float]] = Field(..., description="Keypoints")
    det_score: float = Field(..., description="Detection score")


class Face2Search(NamedTuple):
    """
    face to search, it is a image filled with face for process transfer
    """
    face_img: Image
    bbox: Bbox
    kps: Kps
    det_score: float

    def to_base64(self) -> str:
        """将图像转换为 base64 编码的字符串"""
        return base64.b64encode(self.face_img.tobytes()).decode('utf-8')

    def to_schema(self) -> Face2SearchSchema:
        """将 Face2Search 对象转换为 schema 对象"""
        return Face2SearchSchema(
            face_img=self.to_base64(),
            bbox=self.bbox.tolist(),
            kps=self.kps.tolist(),
            det_score=self.det_score
        )
