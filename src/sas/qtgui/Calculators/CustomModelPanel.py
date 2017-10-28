import datetime
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
        self.model.setItem(W.FUNCTION, QtGui.QStandardItem(""))
        self.model.setItem(W.MATH, QtGui.QStandardItem(""))

        self.model.dataChanged.connect(self.modelChanged)

    def setupMapper(self):
        self.mapper = QtGui.QDataWidgetMapper(self)
        self.mapper.setModel(self.model)
        self.mapper.setOrientation(QtCore.Qt.Vertical)

        self.mapper.addMapping(self.functionName, W.NAME)
        self.mapper.addMapping(self.description, W.DESCRIPTION)
        self.mapper.addMapping(self.params, W.PARAMS)
        self.mapper.addMapping(self.polyParams, W.POLYPARAMS)
        self.mapper.addMapping(self.function, W.FUNCTION)
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

    @staticmethod
    def get_param_helper(param_str):
        """
        yield a sequence of name, value pairs for the parameters in param_str

        Parameters can be defined by one per line by name=value, or multiple
        on the same line by separating the pairs by semicolon or comma.  The
        value is optional and defaults to "1.0".
        """
        for line in param_str.replace(';', ',').split('\n'):
            for item in line.split(','):
                defn, desc = item.split('#', 1) if '#' in item else (item, '')
                name, value = defn.split('=', 1) if '=' in defn else (defn, '1.0')
                if name:
                    yield [v.strip() for v in (name, value, desc)]

    def on_apply(self):
        name = str(self.model.item(W.NAME).text())
        desc = str(self.model.item(W.DESCRIPTION).text())
        name = str(self.model.item(W.NAME).text())
        param_str = str(self.model.item(W.PARAMS).text())
        pd_param_str = str(self.model.item(W.POLYPARAMS).text())
        func_str = str(self.model.item(W.FUNCTION).text())
        
        total = CUSTOM_TEMPLATE.format(
            name=name,
            title="User model for " + name,
            description=desc,
            date=datetime.datetime.now().strftime("%YYY-%mm-%dd"))
        total += "parameters = [ \n"
        total += '#   ["name", "units", default, [lower, upper], "type", "description"],\n'

        param_names = []    # to store parameter names
        pd_params = []
        template = "    ['{name}', '', {value}, [-inf, inf], '', '{desc}'],\n"
        for pname, pvalue, desc in self.get_param_helper(param_str):
            param_names.append(pname)
            total += template.format(name=pname, value=pvalue, desc=desc)
        template = "    ['{name}', '', {value}, [-inf, inf], "\
                   "'volume', '{desc}'],\n"
        for pname, pvalue, desc in self.get_param_helper(pd_param_str):
            param_names.append(pname)
            pd_params.append(pname)
            total += template.format(name=pname, value=pvalue, desc=desc)
        total += "    ]\n"

        total += "def Iq({}):\n".format(", ".join(['x'] + param_names))
        total += '   """Absolute scattering"""\n'
        if "scipy." in func_str:
            total += "    import scipy\n"
        if "numpy." in func_str:
            total += "    import numpy\n"
        if "np." in func_str:
            total += "    import numpy as np\n"
        for func_line in func_str.split("\n"):
            total += "    {}\n".format(func_line)
        total += "## uncomment the following if Iq works for vector x\n"
        total += "#Iq.vectorized = True\n"

        if pd_params:
            total += "\n"
            total += CUSTOM_TEMPLATE_PD.format(
                args=", ".join(pd_params))

        total += "\n"

        total += '#def Iqxy({}):\n'.format(', '.join(["x", "y"] + param_names))
        total += '#    """Absolute scattering of oriented particles."""\n'
        total += '#    ...\n'
        total += '#    return oriented_form(x, y, args)\n'
        total += '## uncomment the following if Iqxy works for vector x, y\n'
        total += '#Iqxy.vectorized = True\n'

        print(total)


CUSTOM_TEMPLATE = '''\
r"""
Definition
----------

Calculates {name}.

{description}

References
----------

Authorship and Verification
---------------------------

* **Author:** --- **Date:** {date}
* **Last Modified by:** --- **Date:** {date}
* **Last Reviewed by:** --- **Date:** {date}
"""

from math import *
from numpy import inf

name = "{name}"
title = "{title}"
description = """{description}"""

'''

CUSTOM_TEMPLATE_PD = '''\
def form_volume({args}):
    """
    Volume of the particles used to compute absolute scattering intensity
    and to weight polydisperse parameter contributions.
    """
    return 0.0

def ER({args}):
    """
    Effective radius of particles to be used when computing structure factors.

    Input parameters are vectors ranging over the mesh of polydispersity values.
    """
    return 0.0

def VR({args}):
    """
    Volume ratio of particles to be used when computing structure factors.

    Input parameters are vectors ranging over the mesh of polydispersity values.
    """
    return 1.0
'''

if __name__ == "__main__":
    APP = QtGui.QApplication([])
    # DO NOT move the following import to the top!
    # (unless you know what you're doing)
    from twisted.internet import reactor
    DLG = CompositeWindow()
    DLG.show()
    APP.exec_()
