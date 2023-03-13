import pandas as pd
import geopandas as gpd
from qgis import processing
import time
from api_ant.core.fun_generales import *
from qgis.PyQt.QtCore import QVariant
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

def clasificaSueloPOT(cantidadSuelos, ced30, claseSueloPOT):
    """
        Función para determinar la clasficación de suelo según 
        la cartografía POT y la Cedula catastral
    """
    clasificaCedCat = ced30[5:7] #Clasificación del suelo según la cedula catastral posiciones 6-7

    if (cantidadSuelos == 1):
        claseSueloPOT = normalizar(claseSueloPOT.values[0]) #quitanto tildes, espacios caracteres especiales y pasando a minusculas
        if(claseSueloPOT == "rural" and clasificaCedCat != "01" ):
            clasificacionPOT = "0"
        elif(claseSueloPOT == "urbano" and clasificaCedCat == "01" ):
            clasificacionPOT = "1"
        elif ("expansion" in claseSueloPOT and clasificaCedCat != "01"):
            clasificacionPOT = "2"
        elif ((claseSueloPOT == "urbano" and clasificaCedCat != "01") 
            or (claseSueloPOT == "rural" and clasificaCedCat == "01")
            or ("expansion" in claseSueloPOT and clasificaCedCat == "01")):
            clasificacionPOT = "4"
    elif (cantidadSuelos > 1):
        clasificacionPOT = "4"
    else:
        clasificacionPOT = "4"

    return clasificacionPOT

def crear_base (df, layer):
    """
        Función para generar la capa de base predial definitiva
        con su respectiva clasificación del suelo POT
    """
    #Extrayendo sistema de referencia del layer
    urip = "polygon?crs=9377&field=id_predial:string"
    
    base = QgsVectorLayer(urip, "base_catastral", 'memory') # Capa de base catastral definitiva
    base.dataProvider().addAttributes([QgsField("id_predial", QVariant.String), 
                                        QgsField("numero_predial", QVariant.String), 
                                        QgsField("numero_predial_anterior", QVariant.String), 
                                        QgsField("clasifica_suelo_pot", QVariant.String),
                                        QgsField("area_terreno_geografica", QVariant.Double)
                                        ])
    base.updateFields()
    #Adicionando el sistema de referencia EPSG:9377
    crs = QgsCoordinateReferenceSystem()
    crs.createFromProj4("+proj=tmerc +lat_0=4 +lon_0=-73 +k=0.9992 +x_0=5000000 +y_0=2000000 +ellps=GRS80 +towgs84=0,0,0,0,0,0,0 +units=m +no_defs")
    base.setCrs(crs)
    
    features = [f for f in layer.getFeatures()] #Datos
    new_features = []

    #Creando un geoDataFrame de la nueva capa Base Catastral POT
    #gdf_baseCPOT = gpd.GeoDataFrame(columns=['id_predial', 'numero_predial', 'numero_predial_anterior', 'clasifica_suelo_pot', "area_terreno_geografica", 'geom'], geometry='geom', crs="EPSG:9377")
    row = {'id_predial': list(), 'numero_predial': list(), 'numero_predial_anterior': list(), 'clasifica_suelo_pot': list(), 'area_terreno_geografica': list(), 'geometry': list()}
    for i in range(len(features)):
        feat = features[i]
        id = str(feat['id_predial']) #de la base inicial antes del intercept
        area = feat['area_terreno_geografica']
        ced30 = feat['numero_predial'] #de la base inicial antes del intercept 
        ced20 = feat['numero_predial_anterior'] #de la base inicial antes del intercept
        claseSueloPOT = df[df['id_predial'] == id]['clase_suelo'] # Filtrando la información del intercept por id predial
        cantidadSuelos = len(claseSueloPOT) # Cuantas clases de suelo que tiene el predio
        clasificacionPOT = clasificaSueloPOT(cantidadSuelos, ced30, claseSueloPOT)
        # Guardando información en la base catastral definitiva
        featBase = QgsFeature() # features
        featBase.setFields(base.fields()) # features con campos de la base definitiva

        featBase.setAttribute('id_predial', id)
        featBase.setAttribute('numero_predial', ced30)
        featBase.setAttribute('numero_predial_anterior', ced20)
        featBase.setAttribute('clasifica_suelo_pot', clasificacionPOT)
        featBase.setAttribute('area_terreno_geografica', area)
        geom = feat.geometry()

        featBase.setGeometry(geom)
        new_features.append(featBase)

        if ced30 == None:
            ced30 = ""
        elif ced20 == None:
            ced20 = ""

        row['id_predial'].append(id)
        row['numero_predial'].append(ced30)
        row['numero_predial_anterior'].append(ced20)
        row['clasifica_suelo_pot'].append(clasificacionPOT)
        row['area_terreno_geografica'].append(area)
        row['geometry'].append(geom)

    base.dataProvider().addFeatures(new_features)
    base.updateExtents()
    base.updateFields()    
    base.commitChanges()
    
    gdf_baseCPOT = gpd.GeoDataFrame(row, geometry='geometry', crs="EPSG:9377")

    return base, gdf_baseCPOT

def baseCatastral_CartoPOT(textEdit, baseCatastral, cartoPOT, output):
    """
        Función para realizar cruce espacial y alfanumerico entre la 
        base catastral y la cartografía POT
    """
    print(" -   1.1 Corrigiendo geometrias y reprojectando CTM12-EPSG:9377 ")
    #Corrigiendo geometrias    
    fix_baseC = processing.run("native:fixgeometries", {'INPUT':baseCatastral,'OUTPUT':'TEMPORARY_OUTPUT'})['OUTPUT']
    fix_CartoPot = processing.run("native:fixgeometries", {'INPUT':cartoPOT,'OUTPUT':'TEMPORARY_OUTPUT'})['OUTPUT']
    time.sleep(2)
    # adicionando al projecto
    #QgsProject.instance().addMapLayer(fix_baseC)
    #QgsProject.instance().addMapLayer(fix_CartoPot)

    #Reprojectando
    baseC_rp = processing.run('native:reprojectlayer', {'INPUT': fix_baseC, 'TARGET_CRS': 'EPSG:9377', 'OUTPUT': 'memory:BaseReprojec'})['OUTPUT']
    time.sleep(2)
    CartoPot_rp = processing.run('native:reprojectlayer', {'INPUT': fix_CartoPot, 'TARGET_CRS': 'EPSG:9377', 'OUTPUT': 'memory:CartoPOTReprojec'})['OUTPUT']
    time.sleep(2)

    # adicionando al projecto
    QgsProject.instance().addMapLayer(baseC_rp)
    QgsProject.instance().addMapLayer(CartoPot_rp)
    
    #removiendo los layer temporales de geometrias corregidas
    #QgsProject.instance().removeMapLayer(fix_baseC)
    #QgsProject.instance().removeMapLayer(fix_CartoPot)
    
    # Creando el campo 'id_predial' 
    print(" -   1.2 Creando y calculando el campo 'id_predial' y  'area_terreno_geografica' en Base Catastral")
    time.sleep(1)
    print(" - - -  Campo 'area_terreno_geografica'")
    baseC_rp_f1 = processing.run('native:fieldcalculator', {'FIELD_LENGTH' : 0, 'FIELD_NAME' : 'area_terreno_geografica', 'FIELD_PRECISION' : 0, 'FIELD_TYPE' : 0, 'FORMULA' : 'area($geometry)', 'INPUT' : baseC_rp, 'OUTPUT' : 'TEMPORARY_OUTPUT' })['OUTPUT']
    time.sleep(1)
    print(" - - -  Campo 'id_predial'")
    baseC_rp_f2 = processing.run('native:fieldcalculator',{'FIELD_LENGTH' : 10, 'FIELD_NAME' : 'id_predial', 'FIELD_PRECISION' : 0, 'FIELD_TYPE' : 2, 'FORMULA' : "lpad($id,10,'0')", 'INPUT' : baseC_rp_f1, 'OUTPUT' : 'TEMPORARY_OUTPUT' })['OUTPUT']
    time.sleep(1)

    #Intercepcion Base Catastral con Cartografía POT
    print(" -   1.3 Intercepcion Base Catastral con Cartografía POT")
    inputFields = ["numero_predial_anterior", "numero_predial", 'id_predial']
    overlayfields = ["clase_suelo"]
    baseCpot = processing.run("native:intersection",{
            'INPUT':baseC_rp_f2, 
            'OVERLAY':CartoPot_rp,
            'INPUT_FIELDS': inputFields,
            'OVERLAY_FIELDS': overlayfields,
            'OUTPUT': 'TEMPORARY_OUTPUT'})['OUTPUT']
    time.sleep(1)
    
    # adicionando al projecto
    QgsProject.instance().addMapLayer(baseCpot)
    
    #Extrayendo información del intercept
    print(" -   1.4 Extrayendo información del intercept")
    cols = ['id_predial', "clase_suelo"] #Nombres columnas que se necesitan
    data = ([f[col] for col in cols] for f in baseCpot.getFeatures()) #Datos

    #Creando un Dataframe del intercept
    df = pd.DataFrame.from_records(data=data, columns=cols)
    
    # Calulando la clasificación suelo POT y exportando Base catastral definitiva
    print(" -   1.5 Calulando la clasificación suelo POT y exportando Base catastral POT")
    baseCastastralPOT, gdf_baseCPOT = crear_base(df, baseC_rp_f2)
    
    #Guardando el layer
    path_output = "".join([output, "/base_catastral.gpkg"])
    QgsVectorFileWriter.writeAsVectorFormat(baseCastastralPOT, path_output,'utf-8')
    
    #removiendo los layer temporales de capas reproyectadas
    QgsProject.instance().removeMapLayer(baseC_rp)
    QgsProject.instance().removeMapLayer(CartoPot_rp)
    QgsProject.instance().removeMapLayer(baseCpot)
    #baseCastastralPOT = QgsVectorLayer(path_output, "base_catastral", 'ogr')
    #QgsProject.instance().addMapLayer(baseCastastralPOT)

    return gdf_baseCPOT