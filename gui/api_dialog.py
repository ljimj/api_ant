from PyQt5 import uic, QtWidgets
import os
from qgis.core import QgsProject, QgsMapLayerProxyModel
             
from api_ant.core.base_catastral_pot import baseCatastral_CartoPOT
from api_ant.core.r1_r2 import r1_r2
from api_ant.core.catastro_unificado import catastro_unificado
from api_ant.core.interrelacion_cat_reg import catastro_SNR

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
        #self.textEdit = self.textEdit

        self.pb_ejecutar.clicked.connect(self.ejecutar)
        self.pb_cancelar.clicked.connect(self.cancel)
     
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
        
        print("\n\n#### ------  Analisis Predial Integral V.0 ------ ####\n\n")

        base_catastral_name = self.mlcb_base_cat.currentText() #nombre layer base catastral
        carto_pot_name = self.mlcb_carto_pot.currentText() #nombre layer cartografía POT

        path_outputs = self.le_outputs.text() #Ruta outputs
        path_insumos = self.le_insumos.text() #Ruta insumos

        base_catastral = QgsProject.instance().mapLayersByName(base_catastral_name)[0] #Layer base catastral
        carto_pot = QgsProject.instance().mapLayersByName(carto_pot_name)[0] #Layer cartografía POT

        # 1. Cruce Base catastral y cartografía POT
        print("1. Cruce Base Catastral y Cartografía POT".upper())
        gdf_baseCPOT = baseCatastral_CartoPOT("", base_catastral, carto_pot, path_outputs)
        # 2. Unión entre R1 y R2
        print("\n\n2. Cruce R1 y R2".upper())
        df_r1r2 = r1_r2(path_insumos, "self.textEdit", path_outputs)
        # 3. Catastro Unificado: Cruce paso 1 y 2
        print("\n\n3. Catastro Unificado: Base Carto POT y Unificado R1-R2".upper())
        gdf_CatUnificado = catastro_unificado("self.textEdit", df_r1r2, gdf_baseCPOT, path_outputs)
        # 4. Interrelación entre catastro y registro
        print("\n\n4. Catastro Unificado y SNR".upper())
        df_api_preliminar = catastro_SNR("self.textEdit", path_insumos, gdf_CatUnificado, path_outputs)
        
        print("      ---------------------")
        print("      |-    By: ljimj    -|")
        print("      ---------------------")
    
    def cancel(self):
        print("cancelado")
        self.close()