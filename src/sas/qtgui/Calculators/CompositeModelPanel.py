from PyQt4 import QtCore
from PyQt4 import QtGui
from PyQt4 import QtWebKit

from twisted.internet import threads
from twisted.internet import reactor

# sas-global
from sas.sascalc.invariant import invariant
import sas.qtgui.Utilities.GuiUtils as GuiUtils
from sas.sascalc.fit.models import ModelManager

# local
from UI.Composite import Ui_CompositeModelPanel

class CompositeWindow(QtGui.QDialog, Ui_CompositeModelPanel):
    # The controller which is responsible for managing signal slots connections
    # for the gui and providing an interface to the data model.
    name = "Composite"  # For displaying in the combo box

    #def __init__(self, manager=None, parent=None):
    def __init__(self, parent=None):
        super(CompositeWindow, self).__init__()
        self.setupUi(self)

        self.setWindowTitle("Composite Model Creator")

        self.modelManager = ModelManager()
        models = self.modelManager.get_model_list()
        for k in models:
            self.model1.addItem("_"+k, None)
            self.model2.addItem("_"+k, None)
            for m in models[k]:
                self.model1.addItem(m.name, m)
                self.model2.addItem(m.name, m)

if __name__ == "__main__":
    APP = QtGui.QApplication([])
    # DO NOT move the following import to the top!
    # (unless you know what you're doing)
    from twisted.internet import reactor
    DLG = CompositeWindow()
    DLG.show()
    APP.exec_()
