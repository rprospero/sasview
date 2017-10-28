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
from sas.qtgui.Perspectives.Fitting.ModelUtilities import ModelManager, find_plugins_dir

# local
from UI.custom import Ui_ModelEditor

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

class CustomModelPanel(QtGui.QDialog, Ui_ModelEditor):
    # The controller which is responsible for managing signal slots connections
    # for the gui and providing an interface to the data model.
    name = "Custom"  # For displaying in the combo box

    #def __init__(self, manager=None, parent=None):
    def __init__(self, parent=None):
        super(CustomModelPanel, self).__init__()
        self.setupUi(self)

        self.setWindowTitle("Custom Model Editor")

        self.setupSignals()
        self.setupModel()
        self.setupMapper()

    def setupSignals(self):
        self.closeBtn.clicked.connect(self.close)
        self.applyBtn.clicked.connect(self.on_apply)

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

        # self.mapper.addMapping(self.functionName, W.NAME)
        # self.mapper.addMapping(self.functionDescription, W.DESCRIPTION)
        # self.mapper.addMapping(self.model1, W.MODEL1)
        # self.mapper.addMapping(self.model2, W.MODEL2)
        # self.mapper.addMapping(self.op, W.OPERATOR)

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

    def on_apply(self):
        pass



if __name__ == "__main__":
    APP = QtGui.QApplication([])
    # DO NOT move the following import to the top!
    # (unless you know what you're doing)
    from twisted.internet import reactor
    DLG = CompositeWindow()
    DLG.show()
    APP.exec_()
