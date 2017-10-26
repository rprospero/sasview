from PyQt4 import QtCore
from PyQt4 import QtGui
from PyQt4 import QtWebKit

from twisted.internet import threads
from twisted.internet import reactor

# sas-global
from sas.sascalc.invariant import invariant
import sas.qtgui.Utilities.GuiUtils as GuiUtils

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

if __name__ == "__main__":
    APP = QtGui.QApplication([])
    import qt4reactor
    # DO NOT move the following import to the top!
    # (unless you know what you're doing)
    from twisted.internet import reactor
    DLG = CompositeWindow(reactor)
    DLG.show()
    reactor.run()
