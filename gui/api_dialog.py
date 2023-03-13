from PyQt5 import uic, QtWidgets
import os
from qgis.core import QgsProject, QgsMapLayerProxyModel
             
from api_ant.core.base_catastral_pot import *

DialogBase, DialogType = uic.loadUiType(
    os.path.join(os.path.dirname( __file__ ), 'api_ant_dialog.ui')
    )

class ApiDialog(DialogBase, DialogType):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("Análisis Predial Integral")

        self.mlcb_base_cat.setFilters(QgsMapLayerProxyModel.PolygonLayer)
        self.mlcb_carto_pot.setFilters(QgsMapLayerProxyModel.PolygonLayer)

        self.pb_insumos.clicked.connect(self.get_insumos_path)
        self.pb_outputs.clicked.connect(self.get_output_path)
        self.textEdit = self.textEdit

        self.pb_ejecutar.clicked.connect(self.ejecutar)
     
    def get_insumos_path(self):
        # Carpeta de Insumos
        folder_path = QtWidgets.QFileDialog.getExistingDirectory(None, "Seleccione una carpeta")
        if folder_path:
            self.le_insumos.setText('{}'.format(folder_path))
            return folder_path
    
    def get_output_path(self):
        # Carpeta de Insumos
        folder_path = QtWidgets.QFileDialog.getExistingDirectory(None, "Seleccione una carpeta")
        if folder_path:
            self.le_outputs.setText('{}'.format(folder_path))
            return folder_path
        
    def ejecutar(self):
        self.textEdit.append("\n\n ### Análisis Predial Integral ###\n\n")
        base_catastral_name = self.mlcb_base_cat.currentText()
        carto_pot_name = self.mlcb_carto_pot.currentText()
        path_outputs = self.le_outputs.text()
        base_catastral = QgsProject.instance().mapLayersByName(base_catastral_name)[0]
        carto_pot = QgsProject.instance().mapLayersByName(carto_pot_name)[0]
        gdf_baseCPOT = baseCatastral_CartoPOT(self.textEdit, base_catastral, carto_pot, path_outputs)
    
    def cancel(self):
        print("cancelado")
        self.close()