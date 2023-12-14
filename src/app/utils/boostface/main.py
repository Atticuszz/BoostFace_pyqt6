"""
-*- coding: utf-8 -*-
@Organization : SupaVision
@Author       : 18317
@Date Created : 14/12/2023
@Description  :
"""
from src.app.utils.boostface.component.camera import CameraWorker
from src.app.utils.boostface.component.common import ClosableQueue
from src.app.utils.boostface.component.detector import DetectorWorker
from src.app.utils.boostface.component.identifier import IdentifyWorker


class BoostFace:
    """
    worker start by signalBus
    """

    def __init__(self):
        self._camera = CameraWorker()
        self._detector = DetectorWorker()
        self._identifier = IdentifyWorker()

    def start(self):
        """start all work threads"""
        self._camera.start()
        self._detector.start()
        self._identifier.start()

    def stop(self):
        """stop all work threads"""
        self._camera.stop_thread()
        self._detector.stop_thread()
        self._identifier.stop_thread()

    def image_queue(self) -> ClosableQueue:
        """get image from camera"""

        return self._identifier.result_queue
