# coding=utf-8
from PyQt6.QtCore import QTimer

from src.app.common.client import WebSocketThread
from src.app.view.component.system_monitor import SystemMonitor

__all__ = ['create_cloud_system_monitor']


class CloudSystemStats(WebSocketThread):
    """
    Remote system stats
    """

    def __init__(self):
        super().__init__(ws_type="cloud_system_monitor")
        self.last_net_io = 0
        self.cpu_percent = 0
        self.ram_percent = 0
        self.net_throughput = 0
        self.start()

    def receive(self, data: dict | str):
        if not isinstance(data, dict):
            raise TypeError("data must be dict")
        self.cpu_percent = float(data['cpu_percent'])
        self.ram_percent = float(data['ram_percent'])
        self.net_throughput = float(data['net_throughput'])


class CloudSystemMonitorC:
    """ Controller for remote system monitor"""

    def __init__(self, view: SystemMonitor, model: CloudSystemStats):
        self.view = view
        self.model = model
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_system_stats)

        self.timer.start(1000)

    def update_system_stats(self):
        """update cloud system stats"""
        cpu_percent = self.model.cpu_percent
        ram_percent = self.model.ram_percent
        net_throughput = self.model.net_throughput
        self.view.update_stats(cpu_percent, ram_percent, net_throughput)


def create_cloud_system_monitor(parent=None) -> CloudSystemMonitorC:
    """create remote system monitor"""
    created_model = CloudSystemStats()
    created_view = SystemMonitor(parent=parent)
    created_controller = CloudSystemMonitorC(created_view, created_model)

    return created_controller
