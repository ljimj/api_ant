# -*- coding: utf-8 -*-

"""
************************************************************************
*                                                                      *
*               ## Análisis Predial Integral - API ##                  *
*    Programa para automatizar la generación de la matriz API          *
*                     ANT - SPO - equipo SIG                           *
*                        Febrero 2023 V.0                              *
*                              ljimj                                   *
*                                                                      *
************************************************************************
"""

__author__ = 'Leonardo Jimenez Joven'

from qgis.PyQt.QtCore import QCoreApplication
from qgis.PyQt.QtCore import QVariant
import pandas as pd
import geopandas as gpd
import time
from qgis import processing
from core.fun_generales import *
from core.base_catastral_pot import *
from qgis.core import (
                       QgsCoordinateReferenceSystem,
                       QgsCoordinateTransform, 
                       QgsProcessing,
                       QgsFeatureSink,
                       QgsProcessingException,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFeatureSink,
                       QgsProcessingParameterFolderDestination,
                       QgsProcessingParameterFile,
                       QgsExpression,
                       QgsExpressionContext,
                       QgsExpressionContextUtils,
                       QgsProject,
                       QgsVectorLayer,
                       QgsField,
                       QgsFeatureRequest,
                       QgsMessageLog,
                       QgsFeature,
                       QgsWkbTypes,
                       QgsVectorFileWriter,
                       QgsGeometry,
                       QgsPointXY,
                       QgsVectorLayerJoinInfo)




class AnalisisPredialIntegral(QgsProcessingAlgorithm):
    """
    This is an example algorithm that takes a vector layer and
    creates a new identical one.

    It is meant to be used as an example of how to create your own
    algorithms and explain methods and variables used to do it. An
    algorithm like this will be available in all elements, and there
    is not need for additional work.

    All Processing algorithms should extend the QgsProcessingAlgorithm
    class.
    """

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    BASEC = 'BASE CATASTRAL'
    CARTOPOT= 'CARTOGRAFIA POT'
    RUTAINSUMOS = "RUTA INSUMOS"
    OUTPUT = 'OUTPUT'

    def tr(self, string):
        """
        Returns a translatable string with the self.tr() function.
        """
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return AnalisisPredialIntegral()

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'API - Análisis Predial Integral'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('API - Análisis Predial Integral')

    def group(self):
        """
        Returns the name of the group this algorithm belongs to. This string
        should be localised.
        """
        return self.tr('API')

    def groupId(self):
        """
        Returns the unique ID of the group this algorithm belongs to. This
        string should be fixed for the algorithm, and must not be localised.
        The group id should be unique within each provider. Group id should
        contain lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'examplescripts'

    def shortHelpString(self):
        """
        Returns a localised short helper string for the algorithm. This string
        should provide a basic description about what the algorithm does and the
        parameters and outputs associated with it..
        """
        return self.tr("Programa para automatizar la generación de la matriz API")

    def initAlgorithm(self, config=None):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.BASEC,
                self.tr('Base Catastral'),
                [QgsProcessing.TypeVectorPolygon]
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.CARTOPOT,
                self.tr('Cartografía POT'),
                [QgsProcessing.TypeVectorPolygon]
            )
        )

        self.addParameter(
            QgsProcessingParameterFile(
                self.RUTAINSUMOS,
                self.tr('Ruta insumos'),
                behavior = 1
            )
        )

        self.addParameter(
            QgsProcessingParameterFile(
                self.OUTPUT,
                self.tr('Folder de salida'),
                behavior = 1
            )
        )
    


    

    

    

    
        
    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """

        # Retrieve the feature source and sink. The 'dest_id' variable is used
        # to uniquely identify the feature sink, and must be included in the
        # dictionary returned by the processAlgorithm function.
        baseCatastral = self.parameterAsVectorLayer(
            parameters,
            self.BASEC,
            context
        )

        cartoPOT = self.parameterAsVectorLayer(
            parameters,
            self.CARTOPOT,
            context
        )

        insumos = self.parameterAsFile(
            parameters,
            self.RUTAINSUMOS,
            context
        )

        output = self.parameterAsFile(
            parameters,
            self.OUTPUT,
            context
        )
        """
        feedback.pushInfo("1. Cruce Base Catastral y Cartografía POT".upper())
        #Cruce Base Catastral y Cartografía POT Retorna un Geodataframe
        gdf_baseCPOT = self.baseCatastral_CartoPOT(feedback ,baseCatastral, cartoPOT, output)

        feedback.pushInfo("\n\n2. Cruce R1 y R2".upper())
        #Cruce R1 y R2 retorna un df
        df_r1r2 = self.r1_r2(insumos, feedback, output)

        feedback.pushInfo("\n\n3. Catastro Unificado: Base Carto POT y Unificado R1-R2".upper())
        gdf_CatUnificado = self.catastro_unificado(feedback, df_r1r2, gdf_baseCPOT, output)"""

        pathCunificado = "".join([insumos, "/CatastroUnificado_Registros_CartoBase_POT.csv"])
        gdf_CatUnificado = pd.read_csv(pathCunificado, dtype=str, engine='python', error_bad_lines=False)
        gdf_CatUnificado = gdf_CatUnificado.fillna("")
        gdf_CatUnificado = gdf_CatUnificado.replace(to_replace="nan",value="")

        feedback.pushInfo("\n\n4. Catastro Unificado y SNR".upper())
        self.catastro_SNR(feedback, insumos, gdf_CatUnificado, output)

        feedback.pushInfo("\n\n#### ------  Analisis Predial Integral V.0 ------ ####\n\n")
        feedback.pushInfo("      ---------------------")
        feedback.pushInfo("      |-    By: ljimj    -|")
        feedback.pushInfo("      ---------------------")

                 
        return {}
