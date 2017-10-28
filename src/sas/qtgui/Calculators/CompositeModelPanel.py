import os.path
import re
from PyQt4 import QtCore
from PyQt4 import QtGui
from PyQt4 import QtWebKit

from twisted.internet import threads
from twisted.internet import reactor

# sas-global
from sas.sascalc.invariant import invariant
import sas.qtgui.Utilities.GuiUtils as GuiUtils
import sas.qtgui.Utilities.ModelManager as ModelManager

# local
from UI.Composite import Ui_CompositeModelPanel

def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)

W = enum(
    'NAME',
    'DESCRIPTION',
    'MODEL1',
    'MODEL2',
    'OPERATOR'
)

SUM_TEMPLATE = """
from sasmodels.core import load_model_info
from sasmodels.sasview_model import make_model_from_info

model_info = load_model_info('{model1}{operator}{model2}')
model_info.name = '{name}'{desc_line}
Model = make_model_from_info(model_info)
"""

class CompositeWindow(QtGui.QDialog, Ui_CompositeModelPanel):
    # The controller which is responsible for managing signal slots connections
    # for the gui and providing an interface to the data model.
    name = "Composite"  # For displaying in the combo box

    #def __init__(self, manager=None, parent=None):
    def __init__(self, parent=None):
        super(CompositeWindow, self).__init__()
        self.setupUi(self)

        self.setWindowTitle("Composite Model Creator")

        self.setupSampleModels()

        self.setupSignals()
        self.setupModel()
        self.setupMapper()

    def setupSampleModels(self):
        self.m1 = self.m2 = None
        self.modelManager = ModelManager
        models = self.modelManager.get_model_list()
        self.model1.clear()
        self.model2.clear()
        model1 = self.model1.model()
        model2 = self.model2.model()
        for k in models:
            category = QtGui.QStandardItem(k)
            font = category.font()
            font.setBold(True)
            category.setFont(font)
            model1.appendRow(category)
            category = QtGui.QStandardItem(category)
            model2.appendRow(category)
            for m in models[k]:
                value = QtGui.QStandardItem(m.name)
                model1.appendRow(value)
                value = QtGui.QStandardItem(value)
                model2.appendRow(value)

    def setupSignals(self):
        self.closeButton.clicked.connect(self.close)
        self.applyButton.clicked.connect(self.on_apply)
        self.modelManager.signal.modelsChanged.connect(self.setupSampleModels)

    def setupModel(self):
        self.model = QtGui.QStandardItemModel(self)
        self.model.setItem(W.NAME, QtGui.QStandardItem(""))
        self.model.setItem(W.DESCRIPTION, QtGui.QStandardItem(""))
        self.model.setItem(W.MODEL1, QtGui.QStandardItem(""))
        self.model.setItem(W.MODEL2, QtGui.QStandardItem(""))
        self.model.setItem(W.OPERATOR, QtGui.QStandardItem("+"))

        self.model.dataChanged.connect(self.modelChanged)

    def setupMapper(self):
        self.mapper = QtGui.QDataWidgetMapper(self)
        self.mapper.setModel(self.model)
        self.mapper.setOrientation(QtCore.Qt.Vertical)

        self.mapper.addMapping(self.functionName, W.NAME)
        self.mapper.addMapping(self.functionDescription, W.DESCRIPTION)
        self.mapper.addMapping(self.model1, W.MODEL1)
        self.mapper.addMapping(self.model2, W.MODEL2)
        self.mapper.addMapping(self.op, W.OPERATOR)

        self.mapper.toFirst()

    def modelChanged(self, item):
        if item.row() == W.MODEL1:
            result = self._get_model_from_index(
                self.model.item(W.MODEL1).text())
            self.m1 = result
        elif item.row() == W.MODEL2:
            result = self._get_model_from_index(
                self.model.item(W.MODEL2).text())
            self.m2 = result

        self._valid_entry(self.m1, self.model1)
        self._valid_entry(self.m2, self.model2)
        self._valid_entry(self._valid_name(), self.functionName)

    @staticmethod
    def _valid_entry(test, widget):
        invalid = "background-color: rgb(255, 128, 128);\n"
        if test:
            widget.setStyleSheet("")
        else:
            widget.setStyleSheet(invalid)

    def _valid_name(self):
        name = str(self.model.item(W.NAME).text())
        if not re.match('^[A-Za-z_][A-Za-z0-9_]+$', name):
            return False
        models = self.modelManager.get_model_list()
        for k in models:
            for m in models[k]:
                if name == m.name:
                    return False
        return True

    def _get_model_from_index(self, name):
        models = self.modelManager.get_model_list()
        result = None
        for k in models:
            for m in models[k]:
                if name == m.name:
                    result = m
        return result

    def on_apply(self):
        if not (self.m1 and self.m2):
            QtGui.QMessageBox.critical(
                self,
                "Cannot Create Model",
                "Please select two models")
            return
        elif not self._valid_name():
            QtGui.QMessageBox.critical(
                self,
                "Cannot Create Model",
                "Please choose a different name")
            return
        description = str(self.model.item(W.DESCRIPTION).text())
        if description.strip() != "":
            description = "\nmodel_info.description = '{}'".format(description)
        output = SUM_TEMPLATE.format(
            name=self.model.item(W.NAME).text(),
            model1=self.model.item(W.MODEL1).text(),
            model2=self.model.item(W.MODEL2).text(),
            operator=self.model.item(W.OPERATOR).text(),
            desc_line=description)
        path = os.path.join(ModelManager.find_plugins_dir(),
                            str(self.model.item(W.NAME).text())+".py")
        with open(path, "w") as outfile:
            outfile.write(output)

        self.modelManager.update()
        self.close()



if __name__ == "__main__":
    APP = QtGui.QApplication([])
    # DO NOT move the following import to the top!
    # (unless you know what you're doing)
    from twisted.internet import reactor
    DLG = CompositeWindow()
    DLG.show()
    APP.exec_()
