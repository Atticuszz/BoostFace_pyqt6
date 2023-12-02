# coding: utf-8
from PyQt6.QtCore import QUrl, QSize
from PyQt6.QtGui import QIcon, QDesktopServices
from PyQt6.QtWidgets import QApplication
from qfluentwidgets import FluentIcon as FIF
from qfluentwidgets import (
    NavigationAvatarWidget,
    NavigationItemPosition,
    MessageBox,
    FluentWindow,
    SplashScreen)

from .cloud_dev_interface import CloudDevInterface
from .gallery_interface import GalleryInterface
from .home_interface import HomeInterface
from .local_dev_interface import LocalDevInterface
from .setting_interface import SettingInterface
from ..common.config import SUPPORT_URL, cfg
from ..common.signal_bus import signalBus
from ..common.translator import Translator


class MainWindow(FluentWindow):

    def __init__(self):
        super().__init__()

        self.splashScreen = None
        self.initWindow()

        # create sub interface
        self.homeInterface = HomeInterface(self)

        self.local_console_interface = LocalDevInterface(self)
        self.settingInterface = SettingInterface(self)
        self.cloudInterface = CloudDevInterface(self)

        # enable acrylic effect
        self.navigationInterface.setAcrylicEnabled(True)

        self.connectSignalToSlot()

        # add items to navigation interface
        self.initNavigation()
        self.splashScreen.finish()

    def connectSignalToSlot(self):
        signalBus.micaEnableChanged.connect(self.setMicaEffectEnabled)
        signalBus.switchToSampleCard.connect(self.switchToSample)
        signalBus.supportSignal.connect(self.onSupport)

    def initNavigation(self):
        # add navigation items
        t = Translator()
        self.addSubInterface(self.homeInterface, FIF.HOME, self.tr('Home'))
        self.navigationInterface.addSeparator()
        self.addSubInterface(
            self.cloudInterface,
            FIF.CLOUD,
            self.tr('Cloud Dev'))

        self.addSubInterface(
            self.local_console_interface,
            FIF.COMMAND_PROMPT,
            self.tr('Local Console'))

        pos = NavigationItemPosition.SCROLL

        # add custom widget to bottom
        self.navigationInterface.addWidget(
            routeKey='avatar',
            widget=NavigationAvatarWidget(
                'zhiyiYo', ':/gallery/images/shoko.png'),
            onClick=self.onSupport,  # TODO: login dialog
            position=NavigationItemPosition.BOTTOM
        )
        self.addSubInterface(
            self.settingInterface,
            FIF.SETTING,
            self.tr('Settings'),
            NavigationItemPosition.BOTTOM)
        self.addSubInterface(
            self.settingInterface,
            FIF.SETTING,
            self.tr('Settings'),
            NavigationItemPosition.BOTTOM)

    def initWindow(self):
        """
        Initialize the window,splash screen and FluentWindow
        """
        # set full screen size
        desktop = QApplication.screens()[0].availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.resize(w, h)
        self.setMinimumWidth(760)

        self.setWindowIcon(QIcon(':/gallery/images/logo.png'))
        self.setWindowTitle('PyQt-Fluent-Widgets')

        self.setMicaEffectEnabled(cfg.get(cfg.micaEnabled))

        # create splash screen
        self.splashScreen = SplashScreen(self.windowIcon(), self)
        self.splashScreen.setIconSize(QSize(106 * 2, 106 * 2))
        self.splashScreen.raise_()

        self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)
        self.show()
        QApplication.processEvents()

    def onSupport(self):
        w = MessageBox(
            '支持作者🥰',
            '个人开发不易，如果这个项目帮助到了您，可以考虑请作者喝一瓶快乐水🥤。您的支持就是作者开发和维护项目的动力🚀',
            self
        )
        w.yesButton.setText('来啦老弟')
        w.cancelButton.setText('下次一定')
        if w.exec():
            QDesktopServices.openUrl(QUrl(SUPPORT_URL))

    def resizeEvent(self, e):
        super().resizeEvent(e)
        if hasattr(self, 'splashScreen'):
            self.splashScreen.resize(self.size())

    def switchToSample(self, routeKey, index):
        """ switch to sample """
        interfaces = self.findChildren(GalleryInterface)
        for w in interfaces:
            if w.objectName() == routeKey:
                self.stackedWidget.setCurrentWidget(w, False)
                w.scrollToCard(index)
