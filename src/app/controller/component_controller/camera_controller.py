# coding=utf-8
# 在 controller.py 文件中
from src.app.model.component_model.camera_model import CameraModel
from src.app.view.component.camera_widget import CameraView, CameraWidget


class CameraController:
    def __init__(self, model: CameraModel, view: CameraView | CameraWidget):
        self.model = model
        self.view = view

        # update image
        self.model.change_pixmap_signal.connect(self.view.cameraCard.update_image)
        # toggle camera
        self.view.cameraCard.toggle_switch.clicked.connect(self.toggle_camera)
        # bind close event

    def toggle_camera(self):
        """
        toggle camera action
        """
        if self.model.isRunning():
            self.model.stop_capture()
        else:
            self.model.start_capture()
            self.view.cameraCard.reset_image()
