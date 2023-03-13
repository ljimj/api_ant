from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import *
import os
from PyQt5.QtWidgets import QAction, QMessageBox
from .gui.api_dialog import ApiDialog

class AnalisisPredialIntegral:
    def __init__(self, iface):
        self.iface = iface

    def initGui(self):
        self.action = QAction(QIcon(
            os.path.join(os.path.dirname(__file__), "icons", "ant.png")
        ),'Análisis Predial Integral', self.iface.mainWindow())
        self.action.setObjectName("Análisis Predial Integral")
        
        self.action.triggered.connect(self.run)
        self.iface.addToolBarIcon(self.action)

    def unload(self):
        self.iface.removeToolBarIcon(self.action)
        del self.action

    def run(self):
        dialog = ApiDialog()
        dialog.exec_()
