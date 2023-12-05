# coding=utf-8
from src.app.model.component_model.result_widget_model import RsultWidgetModel
from src.app.view.component.result_widget import ResultsWidget


class ResultsController:
    def __init__(self, model: RsultWidgetModel, view: ResultsWidget):
        self.model = model
        self.view = view
        self.model.newData.connect(self.view.addTableRow)
        self.model.start()
