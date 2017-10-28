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
    'PARAMS',
    'POLYPARAMS',
    'FUNCTION',
    'MATH',
)


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
        self.model.setItem(W.PARAMS, QtGui.QStandardItem(""))
        self.model.setItem(W.POLYPARAMS, QtGui.QStandardItem(""))
        self.model.setItem(W.MATH, QtGui.QStandardItem("+"))

        self.model.dataChanged.connect(self.modelChanged)

    def setupMapper(self):
        self.mapper = QtGui.QDataWidgetMapper(self)
        self.mapper.setModel(self.model)
        self.mapper.setOrientation(QtCore.Qt.Vertical)

        self.mapper.addMapping(self.functionName, W.NAME)
        self.mapper.addMapping(self.description, W.DESCRIPTION)
        self.mapper.addMapping(self.params, W.PARAMS)
        self.mapper.addMapping(self.polyParams, W.POLYPARAMS)
        self.mapper.addMapping(self.math, W.MATH)

        self.mapper.toFirst()

    def modelChanged(self, item):

        self._valid_entry(
            self._valid_field(
                str(self.model.item(W.NAME).text())),
            self.functionName)

        param = str(self.model.item(W.PARAMS).text()).split(",")
        self._valid_entry(all(map(lambda x: self._valid_field(x),
                                  param)),
                          self.params)
        param = str(self.model.item(W.POLYPARAMS).text()).split(",")
        self._valid_entry(all(map(lambda x: self._valid_field(x),
                                  param)),
                          self.polyParams)
        # self._valid_entry(self._valid_name(), self.functionName)

    def _valid_field(self, x):
        return re.match('^[A-Za-z_][A-Za-z0-9_]+$', x.strip())

    @staticmethod
    def _valid_entry(test, widget):
        invalid = "background-color: rgb(255, 128, 128);\n"
        if test:
            widget.setStyleSheet("")
        else:
            widget.setStyleSheet(invalid)

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
