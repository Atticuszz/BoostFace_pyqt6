# coding: utf-8
import sys
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QApplication, QTableWidgetItem, QWidget, QHBoxLayout
from qfluentwidgets import TableWidget

from src.app.common import signalBus
from src.app.common.client import WebSocketThread
from src.app.types import Image
from src.app.utils.decorator import error_handler

__all__ = ['create_result_widget']


class ResultWidgetModel(WebSocketThread):
    """ Result widget model"""
    newData = pyqtSignal(list)  # Signal to emit new data
    running_signal = signalBus.is_identify_running

    def __init__(self):
        super().__init__(ws_type="identify")
        self.headers = ['ID', 'Name', 'Time']
        self.column_count = len(self.headers)
        self._is_running = False

    @error_handler
    def working(self, data: dict | str | Image):
        """add your working in websocket"""
        if not isinstance(data, dict):
            raise TypeError("data must be dict")
        new_data = [data["id"], data["name"], data["time"]]
        self.newData.emit(new_data)


class ResultsWidget(QWidget):

    def __init__(self, model: ResultWidgetModel | None = None, parent=None):
        super().__init__(parent=parent)
        self.model = model
        self.close_event = None
        # setTheme(Theme.DARK)

        # NOTE: use custom item delegate
        # self.tableView.setItemDelegate(CustomTableItemDelegate(self.tableView))

        # select row on right-click
        # self.tableView.setSelectRightClickedRow(True)

        self._init_ui()
        self.tableView.setColumnCount(self.model.column_count)
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
        if self.model.isRunning():
            signalBus.is_identify_running.emit(False)
            self.close_event()
        super().closeEvent(event)


class ResultsController:
    def __init__(self, model: ResultWidgetModel, view: ResultsWidget):
        self.model = model
        self.view = view
        self.model.newData.connect(self.view.addTableRow)
        self.view.close_event = self.model.stop
        # receive signal from signalBus
        signalBus.is_identify_running.connect(self.model.update_is_running)
        self.model.start()


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
