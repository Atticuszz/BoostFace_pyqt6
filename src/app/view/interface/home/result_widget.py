# coding: utf-8
from typing import Callable

import time

import sys
from PyQt6.QtCore import pyqtSignal, QThread
from PyQt6.QtWidgets import QApplication, QTableWidgetItem, QWidget, QHBoxLayout
from qfluentwidgets import TableWidget

from src.app.common import signalBus
from src.app.common.client.web_socket import WebSocketClient
from src.app.config import qt_logger

__all__ = ['create_result_widget']

from src.app.utils.decorator import error_handler


class ResultWidgetModel(QThread):
    """ Result widget model"""
    newData = pyqtSignal(list)  # Signal to emit new data

    def __init__(self, ws_type="identify"):
        super().__init__()
        self.ws_client = WebSocketClient(ws_type)
        self._is_running = False
        self.headers = ['ID', 'Name', 'Time']
    @error_handler
    def run(self):
        self._is_running = True
        self.ws_client.start_ws()
        while self._is_running:
            data = self.ws_client.receive()
            if data:
                self.process_data(data)
            else:
                time.sleep(0.1)

    def process_data(self, data):
        # 这里处理数据，并通过信号发送
        if isinstance(data, dict):
            new_data = [data[key] for key in self.headers]
            self.newData.emit(new_data)
        else:
            qt_logger.warning(f"identify data type error:{data}")

    def stop(self):
        self._is_running = False
        self.ws_client.stop_ws()
        self.wait()


class ResultsWidget(QWidget):

    def __init__(self, model: ResultWidgetModel | None = None, parent=None):
        super().__init__(parent=parent)
        self.model = model
        self.close_event: Callable[[], None] | None = None
        # setTheme(Theme.DARK)

        # NOTE: use custom item delegate
        # self.tableView.setItemDelegate(CustomTableItemDelegate(self.tableView))

        # select row on right-click
        # self.tableView.setSelectRightClickedRow(True)

        self._init_ui()
        self.tableView.setColumnCount(len(self.model.headers))
        self.tableView.setHorizontalHeaderLabels(self.model.headers)

        self.setStyleSheet("Demo{background: rgb(255, 255, 255)} ")
        # self.hBoxLayout.setContentsMargins(50, 30, 50, 30)
        self.hBoxLayout.addWidget(self.tableView)
        # self.resize(735, 760)

    def _init_ui(self):
        # enable border
        self.hBoxLayout = QHBoxLayout(self)
        self.tableView = TableWidget(self)

        self.tableView.setBorderVisible(True)
        self.tableView.setBorderRadius(8)
        self.tableView.setWordWrap(False)
        self.tableView.verticalHeader().hide()
        self.tableView.resizeColumnsToContents()

    @error_handler
    def addTableRow(self, data: list[str]):
        """
        update table
        """
        row_position = self.tableView.rowCount()
        self.tableView.insertRow(row_position)
        for i, value in enumerate(data):
            self.tableView.setItem(row_position, i, QTableWidgetItem(value))
        # auto resize columns
        self.tableView.resizeColumnsToContents()

    def closeEvent(self, event):
        if self.close_event:
            self.close_event()
        super().closeEvent(event)


class ResultsController:
    def __init__(self, model: ResultWidgetModel, view: ResultsWidget):
        self.model = model
        self.view = view
        # connect to results
        signalBus.identify_results.connect(self.view.addTableRow)
        self.view.close_event = self.model.stop


def create_result_widget(parent=None) -> ResultsController:
    """ create result widget"""
    created_model = ResultWidgetModel()
    created_view = ResultsWidget(created_model, parent=parent)
    created_controller = ResultsController(created_model, created_view)

    return created_controller


if __name__ == "__main__":
    # 示例窗口
    app = QApplication(sys.argv)
    model = ResultWidgetModel()
    demo = ResultsWidget(model)

    controller = ResultsController(model, demo)
    demo.show()
    sys.exit(app.exec())
