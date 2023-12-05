# coding:utf-8
from PyQt6.QtGui import QColor
from qfluentwidgets.components.widgets.acrylic_label import AcrylicLabel

from .gallery_interface import GalleryInterface
from ..common.config import cfg
from ..common.translator import Translator


class MaterialInterface(GalleryInterface):
    """ Material interface """

    def __init__(self, parent=None):
        t = Translator()
        super().__init__(
            title=t.material,
            subtitle='qfluentwidgets.component.widgets',
            parent=parent
        )
        self.setObjectName('materialInterface')

        self.label = AcrylicLabel(
            cfg.get(cfg.blurRadius), QColor(105, 114, 168, 102))
        self.label.setImage(':/gallery/images/chidanta.jpg')
        self.label.setMaximumSize(787, 579)
        self.label.setMinimumSize(197, 145)
        cfg.blurRadius.valueChanged.connect(self.onBlurRadiusChanged)

        self.addExampleCard(
            self.tr('Acrylic label'),
            self.label,
            'https://github.com/zhiyiYo/PyQt-Fluent-Widgets/blob/PyQt6/examples/material/acrylic_label/demo.py',
            stretch=1
        )

    def onBlurRadiusChanged(self, radius: int):
        self.label.blurRadius = radius
        self.label.setImage(':/gallery/images/chidanta.jpg')
