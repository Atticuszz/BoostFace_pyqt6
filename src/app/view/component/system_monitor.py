import sys

import psutil
import pyqtgraph as pg
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QLinearGradient, QColor, QPainter, QBrush
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout
from qfluentwidgets import Theme

from src.app.common.config import cfg


class ResourceGraph(pg.PlotWidget):
    def __init__(self, title: str, unit: str,
                 color: tuple[int, int, int] = (0, 0, 255), parent=None):
        super().__init__(parent=parent)
        if cfg.themeMode.value != Theme.DARK and cfg.themeMode.value != Theme.AUTO:
            self.setBackground('w')
        pg.setConfigOptions(antialias=True)

        # Create the gradient
        self.gradient = QLinearGradient(0, 1, 0, 0)
        self.gradient.setColorAt(1.0, QColor(
            *color, 0))  # Change the color here
        self.gradient.setColorAt(0.0, QColor(
            *color, 150))  # Change the color here
        self.gradient.setCoordinateMode(
            QLinearGradient.CoordinateMode.ObjectBoundingMode)

        self.brush = QBrush(self.gradient)

        self.data = [0] * 100
        self.curve = self.plot(pen=pg.mkPen(QColor(*color), width=2)
                               )  # Change pen color here
        self.curve.setBrush(QBrush(self.gradient))
        self.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Set title and axis labels
        # Set title and axis labels
        self.setTitle(title)
        self.getAxis('left').setLabel('Usage', units=unit)  # 使用传递的单位

    def update_data(self, new_data):
        self.data[:-1] = self.data[1:]
        self.data[-1] = new_data
        self.curve.setData(self.data, fillLevel=0, brush=self.brush)


# 主监控器Widget
class SystemMonitor(QWidget):
    def __init__(self, parent=None):
        super(SystemMonitor, self).__init__(parent)

        self.layout = QVBoxLayout(self)

        # 创建各种资源图表
        self.cpu_graph = ResourceGraph("CPU Usage", "%", (255, 0, 0))
        self.ram_graph = ResourceGraph("RAM Usage", "%", (0, 255, 0))
        self.net_graph = ResourceGraph("Network Throughput", "Bytes/s", (0, 0, 255))

        # 将图表添加到布局中
        self.layout.addWidget(self.cpu_graph)
        self.layout.addWidget(self.ram_graph)
        self.layout.addWidget(self.net_graph)

        # 初始化定时器
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_stats)
        self.timer.start(1000)  # 每秒更新一次

        # 用于计算网络速度的变量
        self.last_net_io = psutil.net_io_counters()

    def update_stats(self):
        # 更新CPU图表
        self.cpu_graph.update_data(psutil.cpu_percent())

        # 更新RAM图表
        self.ram_graph.update_data(psutil.virtual_memory().percent)

        # 更新网络图表
        net_io = psutil.net_io_counters()
        net_send = net_io.bytes_sent - self.last_net_io.bytes_sent
        net_recv = net_io.bytes_recv - self.last_net_io.bytes_recv
        self.last_net_io = net_io

        # 由于是bytes/s，我们不需要累积值，直接显示即时速度
        self.net_graph.update_data(net_send + net_recv)  # 您也可以分别显示发送和接收


if __name__ == '__main__':
    app = QApplication(sys.argv)
    monitor = SystemMonitor()
    monitor.show()
    sys.exit(app.exec())
