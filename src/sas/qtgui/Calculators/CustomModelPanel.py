import datetime
import math
import os.path
import re
import scipy.special
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

        self.model_list = ModelManager.get_model_list()

        self._fill_math_combo()

        self.setupSignals()
        self.setupModel()
        self.setupMapper()

    def setupSignals(self):
        self.closeBtn.clicked.connect(self.close)
        self.applyBtn.clicked.connect(self.on_apply)
        # We can't map the function to the model without
        # losing cursor information, so we need to watch
        # this signal separately.
        self.function.textChanged.connect(
            lambda: self.modelChanged(
                self.model.createIndex(W.FUNCTION, 0)))
        ModelManager.signal.modelsChanged.connect(self.setupSampleModels)

    def setupSampleModels(self):
        self.model_list = ModelManager.get_model_list()

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
        self.mapper.addMapping(self.math, W.MATH)
        # We can't add a mapping to the function, since it causes Qt
        # to lose the cursor position information.

        self.mapper.toFirst()

    def modelChanged(self, item):

        if not self.mapper:
            return
        self.mapper.toFirst()

        if item.row() == W.MATH:
            print(self.function.textCursor())
            print(self.function.textCursor().position())
            self.function.textCursor().insertText(
                str(self.model.item(W.MATH).text()))
            return

        self.applyBtn.setEnabled(True)

        name = str(self.model.item(W.NAME).text())
        self._valid_entry(
            self._valid_name(name),
            self.functionName)

        param = str(self.model.item(W.PARAMS).text())
        param = [x[0] for x in self.get_param_helper(param)]
        self._valid_entry(all(map(lambda x: self._valid_field(x),
                                  param)),
                          self.params)
        param = str(self.model.item(W.POLYPARAMS).text())
        param = [x[0] for x in self.get_param_helper(param)]
        self._valid_entry(all(map(lambda x: self._valid_field(x),
                                  param)),
                          self.polyParams)

        func = str(self.function.toPlainText())
        self._valid_entry("return" in func, self.function)
        # self._valid_entry(self._valid_name(), self.functionName)

    def _fill_math_combo(self):
        idx = 0
        for item in dir(math):
            if item[:2] == "__":
                continue
            if type(getattr(math, item)) is float:
                self.math.addItem(item)
            else:
                self.math.addItem(item+"()")
            self.math.setItemData(
                idx,
                getattr(math, item).__doc__,
                QtCore.Qt.ToolTipRole)
            idx += 1
        # Just to show off, let's also add in the special
        # functions from scipy.  The odds of the users
        # NOT needing some kind of Bessel function are
        # infinitesimal.
        for item in dir(scipy.special):
            if item[0] == "_":
                continue
            if type(getattr(scipy.special, item)) is float:
                self.math.addItem("scipy.special." + item)
            else:
                self.math.addItem("scipy.special." + item + "()")
            self.math.setItemData(
                idx,
                getattr(scipy.special, item).__doc__,
                QtCore.Qt.ToolTipRole)
            idx += 1

    def _valid_field(self, x):
        return re.match('^[A-Za-z_][A-Za-z0-9_]+$', x.strip())

    def _valid_name(self, x):
        if not self._valid_field(x):
            return False
        for k in self.model_list:
            for m in self.model_list[k]:
                if x == m.name or "[plug-in] " + x == m.name:
                    return False
        return True

    def _valid_entry(self, test, widget):
        invalid = "background-color: rgb(255, 128, 128);\n"
        if test:
            widget.setStyleSheet("")
        else:
            widget.setStyleSheet(invalid)
            self.applyBtn.setEnabled(False)

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
        func_str = str(self.function.toPlainText())
        
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
        total += '    """Absolute scattering"""\n'
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

        with open(os.path.join(ModelManager.find_plugins_dir(),
                               name + ".py"), "w") as out:
            out.write(total)

        ModelManager.update()
        self.close()


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
