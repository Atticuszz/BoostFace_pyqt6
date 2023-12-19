"""
-*- coding: utf-8 -*-
@Organization : SupaVision
@Author       : 18317
@Date Created : 14/12/2023
@Description  :
"""
from src.app.common.types import Image
from src.app.utils.boostface.component.camera import Camera
from src.app.utils.boostface.component.detector import Detector
from src.app.utils.boostface.component.drawer import Drawer
from src.app.utils.boostface.component.identifier import Identifier
from src.app.utils.decorator import error_handler


class BoostFace:
    def __init__(self):
        self._camera = Camera()
        self._detector = Detector()
        self._identifier = Identifier()
        self._draw = Drawer()

    @error_handler
    def get_result(self) -> Image:
        """
        :exception CameraOpenError
        :return: Image
        """
        img = self._camera.read()
        detected = self._detector.run_onnx(img)
        identified = self._identifier.identify(detected)
        draw_on = self._draw.show(identified)
        return draw_on

    @error_handler
    def stop_app(self):
        self._camera.stop_device()
        self._identifier.stop_ws_client()
