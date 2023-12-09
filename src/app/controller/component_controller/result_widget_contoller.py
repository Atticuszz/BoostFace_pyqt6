# coding=utf-8
from src.app.common import signalBus
from src.app.model.component_model.result_widget_model import ResultWidgetModel
from src.app.view.component.result_widget import ResultsWidget


class ResultsController:
    def __init__(self, model: ResultWidgetModel, view: ResultsWidget):
        self.model = model
        self.view = view
        self.model.newData.connect(self.view.addTableRow)

        # receive signal from signalBus
        signalBus.is_identify_running.connect(self.model.update_is_running)
        self.model.start()
