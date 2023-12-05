# coding=utf-8
# coding: utf-8
import sys

from PyQt6.QtCore import QModelIndex, Qt
from PyQt6.QtGui import QPalette
from PyQt6.QtWidgets import QApplication, QStyleOptionViewItem, QTableWidgetItem, QWidget, QHBoxLayout
from qfluentwidgets import TableWidget, isDarkTheme, TableItemDelegate

from src.app.model.component_model.result_widget_model import RsultWidgetModel


class CustomTableItemDelegate(TableItemDelegate):
    """ Custom table item delegate """

    def initStyleOption(
            self,
            option: QStyleOptionViewItem,
            index: QModelIndex):
        super().initStyleOption(option, index)
        if index.column() != 1:
            return

        if isDarkTheme():
            option.palette.setColor(
                QPalette.ColorRole.Text,
                Qt.GlobalColor.white)
            option.palette.setColor(
                QPalette.ColorRole.HighlightedText,
                Qt.GlobalColor.white)
        else:
            option.palette.setColor(
                QPalette.ColorRole.Text,
                Qt.GlobalColor.red)
            option.palette.setColor(
                QPalette.ColorRole.HighlightedText,
                Qt.GlobalColor.red)


class ResultsWidget(QWidget):

    def __init__(self, model: RsultWidgetModel | None = None, parent=None):
        super().__init__(parent=parent)
        self.model = model
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

    def closeEvent(self, event):
        if self.model.isRunning():
            self.model.stop()
        super().closeEvent(event)


if __name__ == "__main__":
    from src.app.controller.component_controller.result_widget_contoller import ResultsController

    # 示例窗口
    app = QApplication(sys.argv)
    model = RsultWidgetModel()
    demo = ResultsWidget(model)
    controller = ResultsController(model, demo)
    demo.show()
    sys.exit(app.exec())
