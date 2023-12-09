from src.app.config.config import cfg, HELP_URL, YEAR, AUTHOR, VERSION, FEEDBACK_URL


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
