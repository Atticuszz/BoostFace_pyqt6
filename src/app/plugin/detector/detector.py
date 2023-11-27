# coding=utf-8
from pathlib import Path

from .common import Image2Detect, Face
from .model_router import get_model


class Detector:
    """
    scrfd det_2.5g.onnx with onnxruntime
    """

    def __init__(self):
        root = Path(__file__).parent / 'det_2.5g.onnx'
        self.detector_model = get_model(root, providers=('CUDAExecutionProvider', 'CPUExecutionProvider'))
        prepare_params = {'ctx_id': 0,
                          'det_thresh': 0.5,
                          'input_size': (320, 320)}
        self.detector_model.prepare(**prepare_params)

    def run_onnx(self, img2detect: Image2Detect) -> Image2Detect:
        """
        run onnx model
        :param img2detect:
        :return: img2detect with faces
        """
        detect_params = {'max_num': 0, 'metric': 'default'}
        bboxes, kpss = self.detector_model.detect(img2detect.nd_arr, **detect_params)
        for i in range(bboxes.shape[0]):
            kps = kpss[i] if kpss is not None else None
            bbox = bboxes[i, 0:4]
            det_score = bboxes[i, 4]
            face: Face = Face(bbox, kps, det_score, (0, 0, img2detect.nd_arr.shape[1], img2detect.nd_arr.shape[0]))
            img2detect.faces.append(face)
        return img2detect
