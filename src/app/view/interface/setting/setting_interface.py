# coding:utf-8
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import QWidget, QLabel
from qfluentwidgets import FluentIcon as FIF, setTheme, setThemeColor
from qfluentwidgets import InfoBar
from qfluentwidgets import (
    SettingCardGroup,
    SwitchSettingCard,
    OptionsSettingCard,
    HyperlinkCard,
    PrimaryPushSettingCard,
    ScrollArea,
    ComboBoxSettingCard,
    ExpandLayout,
    CustomColorSettingCard)

from src.app.common import signalBus
from src.app.config.config import cfg, isWin11, HELP_URL, FEEDBACK_URL, YEAR, AUTHOR, VERSION
from src.app.view.style_sheet import StyleSheet

__all__ = ['create_setting_interface']


class SettingModel:
    """
     Setting model
     """

    def __init__(self):
        # Camera settings
        self.camera_fps = cfg.cameraFps
        self.camera_fps_options_texts = [
            '10', '15', '20', '25', '30'
        ]

        self.camera_device = cfg.cameraDevice
        self.camera_device_options_texts = [
            'laptop camera', 'external camera'
        ]

        self.camera_resolution = cfg.cameraResolution
        self.camera_resolution_options_texts = [
            '1920x1080', '1280x720'
        ]

        # theme
        self.theme_mode = cfg.themeMode
        self.theme_color = cfg.themeColor

        # dpi
        self.dpi_scale = cfg.dpiScale

        # language
        self.language = cfg.language

        # update
        self.check_update = cfg.checkUpdateAtStartUp

        # application
        self.help_url = HELP_URL
        self.feedback_url = FEEDBACK_URL
        self.year = YEAR
        self.author = AUTHOR
        self.version = VERSION

    def updateCameraFps(self, fps):
        self.cameraFps = fps
        # 这里可以添加验证、转换等逻辑

    def updateCameraDevice(self, device):
        self.cameraDevice = device


class SettingInterface(ScrollArea):
    """ Setting interface """

    def __init__(self, model: SettingModel, parent=None):
        super().__init__(parent=parent)

        self.model = model
        self.scrollWidget = QWidget()
        self.expandLayout = ExpandLayout(self.scrollWidget)

        # setting label
        self.settingLabel = QLabel(self.tr("Settings"), self)

        # Camera settings
        self.cameraGroup = SettingCardGroup(
            self.tr("Camera"), self.scrollWidget)

        self.cameraFpsCard = OptionsSettingCard(
            self.model.camera_fps,
            FIF.SPEED_HIGH,
            self.tr('Camera FPS'),
            self.tr('Set the FPS of the camera'),
            texts=self.model.camera_fps_options_texts,
            parent=self.cameraGroup
        )
        self.cameraDeviceCard = OptionsSettingCard(
            self.model.camera_device,
            FIF.CAMERA,
            self.tr('Camera device'),
            self.tr('Set the camera device'),
            texts=self.model.camera_device_options_texts,
            parent=self.cameraGroup
        )
        self.cameraResolutionCard = OptionsSettingCard(
            self.model.camera_resolution,
            FIF.PHOTO,
            self.tr('Camera resolution'),
            self.tr('Set the resolution of the camera'),
            texts=self.model.camera_resolution_options_texts,
            parent=self.cameraGroup
        )

        # personalization
        self.personalGroup = SettingCardGroup(
            self.tr('Personalization'), self.scrollWidget)

        self.micaCard = SwitchSettingCard(
            FIF.TRANSPARENT,
            self.tr('Mica effect'),
            self.tr('Apply semi transparent to windows and surfaces'),
            cfg.micaEnabled,
            self.personalGroup
        )

        self.themeCard = OptionsSettingCard(
            self.model.theme_mode,
            FIF.BRUSH,
            self.tr('Application theme'),
            self.tr("Change the appearance of your application"),
            texts=[
                self.tr('Light'), self.tr('Dark'),
                self.tr('Use system setting')
            ],
            parent=self.personalGroup
        )
        self.themeColorCard = CustomColorSettingCard(
            self.model.theme_color,
            FIF.PALETTE,
            self.tr('Theme color'),
            self.tr('Change the theme color of you application'),
            parent=self.personalGroup
        )
        self.zoomCard = OptionsSettingCard(
            self.model.dpi_scale,
            FIF.ZOOM,
            self.tr("Interface zoom"),
            self.tr("Change the size of widgets and fonts"),
            texts=[
                "100%", "125%", "150%", "175%", "200%",
                self.tr("Use system setting")
            ],
            parent=self.personalGroup
        )
        self.languageCard = ComboBoxSettingCard(
            self.model.language,
            FIF.LANGUAGE,
            self.tr('Language'),
            self.tr('Set your preferred language for UI'),
            texts=['简体中文', '繁體中文', 'English', self.tr('Use system setting')],
            parent=self.personalGroup
        )

        # update software
        self.updateSoftwareGroup = SettingCardGroup(
            self.tr("Software update"), self.scrollWidget)
        self.updateOnStartUpCard = SwitchSettingCard(
            FIF.UPDATE,
            self.tr('Check for updates when the application starts'),
            self.tr('The new version will be more stable and have more features'),
            configItem=self.model.check_update,
            parent=self.updateSoftwareGroup)

        # application
        self.aboutGroup = SettingCardGroup(self.tr('About'), self.scrollWidget)
        self.helpCard = HyperlinkCard(
            self.model.help_url,
            self.tr('Open help page'),
            FIF.HELP,
            self.tr('Help'),
            self.tr(
                'Discover new features and learn useful tips about BoostFace'),
            self.aboutGroup
        )
        self.feedbackCard = PrimaryPushSettingCard(
            self.tr('Provide feedback'),
            FIF.FEEDBACK,
            self.tr('Provide feedback'),
            self.tr('Help us improve BoostFace by providing feedback'),
            self.aboutGroup
        )
        self.aboutCard = PrimaryPushSettingCard(
            self.tr('Check update'),
            FIF.INFO,
            self.tr('About'),
            '© ' +
            self.tr('Copyright') +
            f" {self.model.year}, {self.model.author}. " +
            self.tr('Version') +
            " " +
            self.model.version,
            self.aboutGroup)

        self.__initWidget()

    def __initWidget(self):
        self.resize(1000, 800)
        self.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setViewportMargins(0, 80, 0, 20)
        self.setWidget(self.scrollWidget)
        self.setWidgetResizable(True)
        self.setObjectName('settingInterface')

        # initialize style sheet
        self.scrollWidget.setObjectName('scrollWidget')
        self.settingLabel.setObjectName('settingLabel')
        StyleSheet.SETTING_INTERFACE.apply(self)

        self.micaCard.setEnabled(isWin11())

        # initialize layout
        self.__initLayout()

    def __initLayout(self):
        self.settingLabel.move(36, 30)

        # add cards to group
        self.cameraGroup.addSettingCard(self.cameraDeviceCard)
        self.cameraGroup.addSettingCard(self.cameraFpsCard)
        self.cameraGroup.addSettingCard(self.cameraResolutionCard)
        self.personalGroup.addSettingCard(self.micaCard)
        self.personalGroup.addSettingCard(self.themeCard)
        self.personalGroup.addSettingCard(self.themeColorCard)
        self.personalGroup.addSettingCard(self.zoomCard)
        self.personalGroup.addSettingCard(self.languageCard)

        self.updateSoftwareGroup.addSettingCard(self.updateOnStartUpCard)

        self.aboutGroup.addSettingCard(self.helpCard)
        self.aboutGroup.addSettingCard(self.feedbackCard)
        self.aboutGroup.addSettingCard(self.aboutCard)

        # add setting card group to layout
        self.expandLayout.setSpacing(28)
        self.expandLayout.setContentsMargins(36, 10, 36, 0)

        # 1. set into layout
        self.expandLayout.addWidget(self.cameraGroup)
        self.expandLayout.addWidget(self.personalGroup)
        self.expandLayout.addWidget(self.updateSoftwareGroup)
        self.expandLayout.addWidget(self.aboutGroup)

    def _showRestartTooltip(self):
        """ show restart tooltip """
        InfoBar.success(
            self.tr('Updated successfully'),
            self.tr('Configuration takes effect after restart'),
            duration=1500,
            parent=self
        )


class SettingInterfaceC:
    """ Setting interface controller"""

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


# TODO:separate the interface to several parts,Interface should be a class that only contains the layout and widgets
def create_setting_interface(parent=None) -> SettingInterfaceC:
    """
    create setting interface
    :param parent:
    :return:
    """
    created_model = SettingModel()
    created_view = SettingInterface(created_model, parent=parent)
    created_controller = SettingInterfaceC(created_model, created_view)

    return created_controller
