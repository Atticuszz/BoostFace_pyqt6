# coding=utf-8
import random
# coding: utf-8
import sys

from PyQt6.QtCore import QModelIndex, Qt, QThread, pyqtSignal
from PyQt6.QtGui import QPalette
from PyQt6.QtWidgets import QApplication, QStyleOptionViewItem, QTableWidgetItem, QWidget, QHBoxLayout
from qfluentwidgets import TableWidget, isDarkTheme, TableItemDelegate


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


class DataGeneratorThread(QThread):
    newData = pyqtSignal(list)  # Signal to emit new data

    def run(self):
        while True:
            self.sleep(1)  # Wait for 1 second
            data = [
                str(
                    random.randint(
                        1, 100)), "Name {}".format(
                    random.randint(
                        1, 100)), "gender {}".format(
                    random.randint(
                        1, 100)), "Time {}".format(
                    random.randint(
                        1, 100))]
            self.newData.emit(data)  # Emit the signal with new data


class ResultsWidget(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        # setTheme(Theme.DARK)

        # NOTE: use custom item delegate
        # self.tableView.setItemDelegate(CustomTableItemDelegate(self.tableView))

        # select row on right-click
        # self.tableView.setSelectRightClickedRow(True)

        self._init_ui()
        self.tableView.setColumnCount(4)  # 设置为三列

        self.tableView.setHorizontalHeaderLabels(
            ['ID', 'Name', 'gender', 'Time'])

        # 填充表格数据，您需要根据您的需求调整这里的数据
        # Start the data generation thread
        self.dataThread = DataGeneratorThread(self)
        self.dataThread.newData.connect(self.addTableRow)
        self.dataThread.start()

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

    def addTableRow(self, data):
        row_position = self.tableView.rowCount()
        self.tableView.insertRow(row_position)
        for i, value in enumerate(data):
            self.tableView.setItem(row_position, i, QTableWidgetItem(value))


if __name__ == "__main__":
    # 示例窗口
    app = QApplication(sys.argv)
    demo = ResultsWidget()
    demo.show()
    sys.exit(app.exec())
