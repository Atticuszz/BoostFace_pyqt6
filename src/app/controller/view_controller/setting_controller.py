# coding=utf-8
from PyQt6.QtCore import QUrl
from PyQt6.QtGui import QDesktopServices
from qfluentwidgets import setTheme, setThemeColor

from src.app.common import signalBus
from src.app.common.config import cfg
from src.app.model.view_model.setting_model import SettingModel
from src.app.view.interface.setting_interface import SettingInterface


class SettingController:
    def __init__(self, model: SettingModel, view: SettingInterface):
        self.model = model
        self.view = view

        self._init_camera_connect()
        self._init_personalization_connect()
        self._init_application_connect()

    def _init_camera_connect(self):
        """
        inti camera connect
        """
        self.view.cameraFpsCard.optionChanged.connect(self._update_camera_fps)
        self.view.cameraDeviceCard.optionChanged.connect(
            self._update_camera_device)
        self.view.cameraResolutionCard.optionChanged.connect(
            self._update_camera_resolution)

    def _init_personalization_connect(self):
        """
        init personalization connect
        """
        self.view.themeCard.optionChanged.connect(
            lambda ci: setTheme(cfg.get(ci)))
        self.view.themeColorCard.colorChanged.connect(setThemeColor)

        self.view.micaCard.checkedChanged.connect(signalBus.micaEnableChanged)
        # self.view.zoomCard.optionChanged.connect(self.updateZoom)
        # self.view.languageCard.optionChanged.connect(self.updateLanguage)

    def _init_application_connect(self):
        """
        init application connect
        """
        self.view.updateOnStartUpCard.checkedChanged.connect(
            self._update_on_start_up)
        # about
        self.view.feedbackCard.clicked.connect(
            lambda: QDesktopServices.openUrl(QUrl(self.model.feedback_url)))

    def _update_camera_fps(self, fps: str):
        self.model.camera_fps = fps

    def _update_camera_device(self, device: str):
        self.model.camera_device = device

    def _update_camera_resolution(self, resolution: str):
        self.model.camera_resolution = resolution

    def _update_on_start_up(self):
        cfg.appRestartSig.connect(self.view._showRestartTooltip)
