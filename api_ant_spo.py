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
from fuzzywuzzy import fuzz
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
from qgis import processing



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

    
    def calculate_expression(self, layer, field, expression):
        """
            Calcular una expresion según la capa y campo dado
        """
        expression = QgsExpression(expression)
        
        #creando el objeto de QgsExpressionContext
        context = QgsExpressionContext()
        context.appendScopes(QgsExpressionContextUtils.globalProjectLayerScopes(layer))
        
        #editando y calculando el área
        layer.startEditing()
        for f in layer.getFeatures():
            context.setFeature(f)
            exp = expression.evaluate(context)
            f[field] = str(exp).zfill(8) #zfill para rellenar con ceros a la izquierda
            layer.updateFeature(f)  
        layer.commitChanges()
    
    def y_otro(self, list_nombres):
        """
            Función para adicionar la palabra otro a un nombre.
            Esto cuando hayan más de un nombre en a lista
        """
        numero_nombres = len(list_nombres)
        if numero_nombres > 1:
            otro = " Y OTRO"
        else:
            otro = ""
        
        return otro

    def fmi_activo(self, estado):
        """
            Función para retornar el dominio del campo fmi_activo
            según el estado del folio
        """

        estado = estado.strip() #Eliminando espacios en blanco
        estado = estado.lower() # pasando a minusculas

        if(estado == "activo"):
            dominio = "0"
        elif(estado == "cerrado"):
            dominio = "2"
        else:
            dominio = "1"

        return dominio        
 
    def normalizar(self, nombre):
        """
            Función para normalizar nombres buscando y reemplazando
            los caracteres descritos
        """
        nombre = nombre.lower() # pasando el nombre a minusculas
        reemplazos = ( #(Buscar, reemplazar)
            ("á", "a"), ("é", "e"), ("í", "i"), ("ó", "o"), ("ú", "u"), (".", ""),(" y ", " "),
            ("-", ""), ("_", ""), ("*", ""), ("+", ""), ("&", ""), ("'", ""), ('"', ''),
            ("ñ", "n"), ("sucesores", ""), ("sucesor", ""), (" su ", " "), (" suc ", " "), 
            (" del ", " "), ('de los', ' '), ("de la", " "), ("de las", " "), (" de ", " "),
            ("vda de", ""), ('vda', ''), (" cia", ""), ("ltda", "")
        )
        for a, b in reemplazos:
            # Ciclo para aplicar los buscar y remplazar
            nombre = nombre.replace(a, b)
        nombre = nombre.strip() #Eliminando espacios en blanco

        reemplazos_PJ = ( #Reemplazos de palabras para personas jurídicas
            ("agencia - infraestructura", "ani"), (" ani ", "ani"), ("fondo aeronautico", "fan"), 
            (" fan ", "fan"), ("instituto - desarrollo - rural", "incora"), 
            ("instituto - reforma - agraria", "incora"),("instituto - colombia", "incora"),
            ("incod", "incora"), ("incor", "incora"), ("instituto - bienestar", "icbf"), ("icbf", "icbf"),
            ("servicio - aprendizaje", "sena"), ("sena", "sena")
        )

        for a, b in reemplazos_PJ:
            # Ciclo para aplicar los buscar y cambiar el nombre de persona jurídica
            if a in nombre: #Si el nombre contiene la palabra descrita en el elemento a de la tupla (a, b)
                nombre = b # Se asigna al nombre el elemento b

        return nombre
    
    def encontrar_matriz_segregado(self, fmi, df_snr):
        """
            Función para encontrar los folios matriz y segregados
        """
        if(fmi != ""):

            #SEGREGADOS
            fmiListM = df_snr['MATRICULA'].unique().tolist() #Lista de todos los FMI existentes en SNR
            if(fmi in fmiListM): #si el fmi se encuentra en la lista continue

                #Operaciones para determinar los fmi derivados
                df_snr_filterS = df_snr[df_snr['MATRICULA'] == fmi] #Filtro para encontrar segregados del fmi
                list_snrS = set(df_snr_filterS['FOLIO DERIVADO'].tolist()) #Lista de segregados unicos
                segregados = ""
                for segre in list_snrS:
                    if(segre != "" and segre != "nan"):
                        segregados += "{};".format(segre)
            else:
                segregados = ""
            
            #MATRICES
            fmiListD = df_snr['FOLIO DERIVADO'].unique().tolist()
            if(fmi in fmiListD):
                #Operaciones para determinar los fmi matrices
                df_snr_filterM = df_snr[df_snr['FOLIO DERIVADO'] == fmi] #Filtro para encontrar matrices del fmi
                list_snrM = set(df_snr_filterM['MATRICULA'].tolist()) #Lista de Matrices
                matrices = ""
                for matri in list_snrM:
                    if(matri != "" and matri != "nan"):
                        matrices += "{};".format(matri)
            else:
                matrices = ""
            try:
                if (matrices[-1] == ";"):
                    matrices = matrices[:-1]
            except:
                pass
            try:
                if (segregados[-1] == ";"):
                    segregados = segregados[:-1]
            except:
                pass
        else:
            matrices = "" 
            segregados = ""

        return pd.Series([matrices, segregados])
    
    def separarFolio(self, fmi):
        """
            Función para separar los numeros de fmi
            en circulo registral, número de folio y
            folios sistema antiguo
        """
        if "-" in str(fmi):# Si el fmi tiene "-" separar
            fmi = fmi.split("-")
            circulo = fmi[0] 
            folio = fmi[1]
            antiguo = ""
        else: # Si no que el circulo este vacio y el folio igual fmi
            circulo = ""
            folio = ""
            antiguo = fmi
        #print("{} / {}".format(circulo, folio))
        return circulo, folio, antiguo

    def normalizarFMI(self, fmi):
        """
            Función para normalizar los folios de matricula

        """
        fmi = str(fmi)
        guiones = fmi.count("-")
        if fmi == "nan":
            fmi = ""
        
        if guiones == 0:
            #Para folio de sistema antiguo 
            fmi = fmi #544332222
        elif guiones == 1:
            # Para folios actuales
            fmisep = fmi.split("-")
            digCirculo = len(fmisep[0]) #Cantidad de digitos del circulo registral
            if (digCirculo == 2):
                fmi = "0" + fmi #062-34532
            elif (digCirculo == 3):
                fmi = fmi #546-56543
            else:
                fmi = "".join(fmisep) #folio antiguo
        elif guiones > 1:
            #para folios antiguos
            fmisep = fmi.split("-")
            fmi = "".join(fmisep)
        
        return fmi

    def comparaNombres(self, nombre1, nombre2):
        """
            Función para comparar dos nombres
            Si no son exactamente iguales se va establecer
            en qué porcentaje son iguales.
            Si son iguales en un >83% Retorna "IGUAL"
        """
        if (nombre1 != "" or nombre2 != "" or nombre1 != "nan" or nombre2 != "nan"):

            porcentaje = fuzz.ratio(nombre1,nombre2) 
            # Función para comparar palabras retornando un porcentaje 0%-100% de similitud
            if porcentaje > 83:
                comparacion = "IGUAL"
            else:
                comparacion = "DESIGUAL"
        else:
            porcentaje = 0
            comparacion = "DESIGUAL"

        return comparacion, porcentaje
    
    def quitarCeros(self, num): 
        """
            Función para normalizar el documento
            de identidad (quitar ceros)
        """
        num = str(num) # pasando documento a string
        num = num.strip() #Quitando posibles espacios
        numNorm = num.lstrip('+-0') #Quitando ceros a la izquierda
        
        return numNorm

    def crear_base (self, df, layer):
        """
            Función para generar la capa de base predial definitiva
            con su respectiva clasificación del suelo POT
        """
        #Extrayendo sistema de referencia del layer
        tf = "&field=id_predial:string"
        urip = "polygon?crs=9377"+tf
        
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

        #Creando un geoDataFrame de la nueva capa Base Catastral POT
        gdf_baseCPOT = gpd.GeoDataFrame(columns=['id_predial', 'numero_predial', 'numero_predial_anterior', 'clasifica_suelo_pot', "area_terreno_geografica", 'geom'], geometry='geom', crs="EPSG:9377")
        
        featLayer = layer.getFeatures() #features de la capa inicial de base catastral
        for feat in featLayer:

            id = feat['id_predial'] #de la base inicial antes del intercept
            area = feat['area_terreno_geografica']
            ced30 = feat['numero_predial'] #de la base inicial antes del intercept 
            ced20 = feat['numero_predial_anterior'] #de la base inicial antes del intercept
            df_filter = df[df['id_predial'] == id] # Filtrando la información del intercept por id predial
            claseSueloPOT = df_filter['clase_suelo'].tolist()  #obteniendo la clase del suelo por predio del intercept
            cantidadSuelos = len(claseSueloPOT) # Cuantas clases de suelo que tiene el predio
            clasificaCedCat = ced30[5:7] #Clasificación del suelo según la cedula catastral posiciones 6-7

            if (cantidadSuelos == 1):
                claseSueloPOT = self.normalizar(claseSueloPOT[0]) #quitanto tildes, espacios caracteres especiales y pasando a minusculas
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

            # Guardando información en la base catastral definitiva
            featBase = QgsFeature() # features
            featBase.setFields(base.fields()) # features con campos de la base definitiva

            featBase.setAttribute('id_predial', id)
            featBase.setAttribute('numero_predial', ced30)
            featBase.setAttribute('numero_predial_anterior', ced20)
            featBase.setAttribute('clasifica_suelo_pot', clasificacionPOT)
            featBase.setAttribute('area_terreno_geografica', area)
            geom = feat.geometry()

            row = {'id_predial': id, 'numero_predial': ced30, 'numero_predial_anterior': ced20, 'clasifica_suelo_pot': clasificacionPOT, 'area_terreno_geografica': area, 'geom': geom}
            gdf_baseCPOT = gdf_baseCPOT.append(row, ignore_index = True)

            featBase.setGeometry(geom)
            base.dataProvider().addFeature(featBase)
            

        base.commitChanges() 

        return base, gdf_baseCPOT

    def baseCatastral_CartoPOT(self, feedback ,baseCatastral, cartoPOT, output):
        """
            Función para realizar cruce espacial y alfanumerico entre la 
            base catastral y la cartografía POT
        """
        feedback.pushInfo(" -   1.1 Corrigiendo geometrias y reprojectando CTM12-EPSG:9377 ")
        #Corrigiendo geometrias    
        fix_baseC = processing.run("native:fixgeometries", {'INPUT':baseCatastral,'OUTPUT':'TEMPORARY_OUTPUT'})['OUTPUT']
        fix_CartoPot = processing.run("native:fixgeometries", {'INPUT':cartoPOT,'OUTPUT':'TEMPORARY_OUTPUT'})['OUTPUT']
        
        # adicionando al projecto
        #QgsProject.instance().addMapLayer(fix_baseC)
        #QgsProject.instance().addMapLayer(fix_CartoPot)

        #Reprojectando
        baseC_rp = processing.run('native:reprojectlayer', {'INPUT': fix_baseC, 'TARGET_CRS': 'EPSG:9377', 'OUTPUT': 'memory:BaseReprojec'})['OUTPUT']
        CartoPot_rp = processing.run('native:reprojectlayer', {'INPUT': fix_CartoPot, 'TARGET_CRS': 'EPSG:9377', 'OUTPUT': 'memory:CartoPOTReprojec'})['OUTPUT']

        # adicionando al projecto
        QgsProject.instance().addMapLayer(baseC_rp)
        QgsProject.instance().addMapLayer(CartoPot_rp)
        
        #removiendo los layer temporales de geometrias corregidas
        #QgsProject.instance().removeMapLayer(fix_baseC)
        #QgsProject.instance().removeMapLayer(fix_CartoPot)
        
        # Creando el campo 'id_predial' 
        feedback.pushInfo(" -   1.2 Creando y calculando el campo 'id_predial' en Base Catastral")
        baseC_rp.startEditing()
        baseC_rp.dataProvider().addAttributes([QgsField("id_predial", QVariant.String), 
                                                QgsField("area_terreno_geografica", QVariant.Double)])
        baseC_rp.updateFields()
        baseC_rp.commitChanges()

        # calculando id predial
        self.calculate_expression(baseC_rp, "id_predial", '$id')
        # calculando area
        self.calculate_expression(baseC_rp, "area_terreno_geografica", 'area($geometry)')

        #Intercepcion Base Catastral con Cartografía POT
        feedback.pushInfo(" -   1.3 Intercepcion Base Catastral con Cartografía POT")
        inputFields = ["numero_predial_anterior", "numero_predial", 'id_predial']
        overlayfields = ["clase_suelo"]
        baseCpot = processing.run("native:intersection",{
                'INPUT':baseC_rp, 
                'OVERLAY':CartoPot_rp,
                'INPUT_FIELDS': inputFields,
                'OVERLAY_FIELDS': overlayfields,
                'OUTPUT': 'TEMPORARY_OUTPUT'})['OUTPUT']
        
        # adicionando al projecto
        QgsProject.instance().addMapLayer(baseCpot)
        
        #Extrayendo información del intercept
        feedback.pushInfo(" -   1.4 Extrayendo información del intercept")
        cols = [f.name() for f in baseCpot.fields()] #Nombres columnas
        data = ([f[col] for col in cols] for f in baseCpot.getFeatures()) #Datos

        #Creando un Dataframe del intercept
        df = pd.DataFrame.from_records(data=data, columns=cols)
        
        # Calulando la clasificación suelo POT y exportando Base catastral definitiva
        feedback.pushInfo(" -   1.5 Calulando la clasificación suelo POT y exportando Base catastral POT")
        baseCastastralPOT, gdf_baseCPOT = self.crear_base(df, baseC_rp)
        
        #Guardando el layer
        path_output = output + "/base_catastral.gpkg"
        QgsVectorFileWriter.writeAsVectorFormat(baseCastastralPOT, path_output,'utf-8')

        #removiendo los layer temporales de capas reproyectadas
        QgsProject.instance().removeMapLayer(baseC_rp)
        QgsProject.instance().removeMapLayer(CartoPot_rp)
        QgsProject.instance().removeMapLayer(baseCpot)
        #baseCastastralPOT = QgsVectorLayer(path_output, "base_catastral", 'ogr')
        #QgsProject.instance().addMapLayer(baseCastastralPOT)

        return gdf_baseCPOT

    def r1_r2(self, insumos, feedback, output):
        """
            Función para unificar los registros 1 y 2
        """

        pathR1 = insumos + "/Registro 1.xlsx"
        pathR2 = insumos + "/Registro 2.xlsx"

        feedback.pushInfo(" - 2.1 Leyendo R1")
        df_r1 = pd.read_excel(pathR1)
        feedback.pushInfo(" - 2.2 Leyendo R2")
        df_r2 = pd.read_excel(pathR2)

        # -- Atributos de la unificación -- 
        # "DEPARTAMENTO" "MUNICIPIO" "NUMERO DE PREDIO" "Cedula Castastral 20" 
        # "Cedula Castastral 30" "NOMBRE" "NUMERO DOCUMENTO" "DIRECCION" 
        # "MATRICULA INMOBILIARIA" "AREA TERRENO" "AREA CONSTRUIDA"
        
        # Creando un dataframe donde se almacenaran la unión
        feedback.pushInfo(" - 2.3 Unificando por Cedula Catastral (30 dig)")
        df_r1r2 = df_r2[["numero_predial", "MATRICULA INMOBILIARIA"]].merge(df_r1[["DEPARTAMENTO", "MUNICIPIO", "NUMERO DE PREDIO", "numero_predial_anterior","numero_predial", "NOMBRE", "NUMERO DOCUMENTO", "DIRECCION", "AREA TERRENO", "AREA CONSTRUIDA"]], on = "numero_predial", how = "outer")
        
        # exportando resultado a excel
        feedback.pushInfo(" - 2.4 exportando resultado a excel")
        xlsPath = output + "/Unificado_Registros12.xlsx"
        df_r1r2.to_excel(xlsPath)

        return df_r1r2

    def catastro_unificado(self, feedback, df_r1r2, gdf_baseCPOT, output):
        """
            Función para realizar cruce por cedula catastral entre 
            la base catastral POT y la unificada de los registros 1 y 2
        """
        # Creando un dataframe donde se almacenaran la unión
        feedback.pushInfo(" - 3.1 Cruzando por Cedula Catastral (30 dig)")
        gdf_CatUnificado = gdf_baseCPOT[["id_predial", "numero_predial", "clasifica_suelo_pot", "area_terreno_geografica", "geom"]].merge(df_r1r2[["DEPARTAMENTO", "MUNICIPIO", "MATRICULA INMOBILIARIA", "NUMERO DE PREDIO", "numero_predial_anterior","numero_predial", "NOMBRE", "NUMERO DOCUMENTO", "DIRECCION", "AREA TERRENO", "AREA CONSTRUIDA"]], on = "numero_predial", how = "outer")

        feedback.pushInfo(" - 3.2 Quitando ceros y duplicados (CedulaCatastral-FMI-Nombre)")
        gdf_CatUnificado["numero_predial"] = gdf_CatUnificado.apply(lambda x: self.quitarCeros(x["numero_predial"]), axis=1)
        gdf_CatUnificado["MATRICULA INMOBILIARIA"] = gdf_CatUnificado.apply(lambda x: self.quitarCeros(x["MATRICULA INMOBILIARIA"]), axis=1)
        gdf_CatUnificado["MATRICULA INMOBILIARIA"] = gdf_CatUnificado.apply(lambda x: self.normalizarFMI(x["MATRICULA INMOBILIARIA"]), axis=1)
        gdf_CatUnificado["NUMERO DOCUMENTO"] = gdf_CatUnificado.apply(lambda x: self.quitarCeros(x["NUMERO DOCUMENTO"]), axis=1)
        gdf_CatUnificado["NOMBRE"] = gdf_CatUnificado["NOMBRE"].str.strip()
        gdf_CatUnificado["CedCat-FMI-Nom"] = gdf_CatUnificado.apply(lambda x: str(x["numero_predial"]) + "-" + str(x["MATRICULA INMOBILIARIA"]) + "-" + str(x["NOMBRE"]), axis =1)
        # exportando resultado a excel
        feedback.pushInfo(" - 3.3 exportando resultado a excel")
        xlsPath = output + "/antes_CatastroUnificado_Registros_CartoBase_POT.xlsx"
        gdf_CatUnificado.to_excel(xlsPath)
        gdf_CatUnificado = gdf_CatUnificado.drop_duplicates(subset=['CedCat-FMI-Nom'])

        # exportando resultado a excel
        feedback.pushInfo(" - 3.4 exportando resultado a excel depues de eliminar duplicados")
        xlsPath = output + "/CatastroUnificado_Registros_CartoBase_POT.xlsx"
        gdf_CatUnificado.to_excel(xlsPath)

        return gdf_CatUnificado

    def fmiCat_enSNR(self, cedCat_fmi_list, gdf_CatUnificado, snr_fmi_list, df_snr, feedback):
        """
            Folios de Catastro presentes en SNR (según concat cedula_cat_fmi)
        """
        #Creando df de API vacion para empezar a llenar con los registros
        df_api = pd.DataFrame(columns=[
                    "fmi", "id_predial", "departamento", "municipio", "numero_predial",  
                    "numero_predial_anterior", "circulo_registral", "numero_matricula", 
                    "antiguo_sistema_registro", "interrelacion_cat_reg", 
                    "area_terreno_r1", "area_construida_r1", "area_terreno_geografica",
                    "clasificacion_suelo_pot", "ultimo_propietario_fmi", "direccion"
                ])
        
        #Creando un df para la comparación de nombres y poder exportar a xls
        df_comparacion = pd.DataFrame(columns=["Nombre SNR", "Nombre Catastro", "Porcentaje"])

        for datoCatastro in cedCat_fmi_list:
            
            #Filtrando por cedula_cat_fmi            
            gdf_CatUnificadoFilter = gdf_CatUnificado[gdf_CatUnificado['cedCat_fmi'] == datoCatastro]
            # Extrayendo información de catastro unificado
            list_DocsID_Cat = gdf_CatUnificadoFilter["NUMERO DOCUMENTO"].tolist() # Lista Documentos de identidad Catastro Unificado
            list_noms_Catastro = gdf_CatUnificadoFilter["NOMBRE"].tolist() #Lista Nombres Catastro Unificado
            
            list_noms_Catastro = [str(nombre).replace("nan", "") for nombre in list_noms_Catastro] #Quitando valores con nan

            #feedback.pushInfo(" - - - tamaño filtro cat {}".format(len(gdf_CatUnificadoFilter)))
            #feedback.pushInfo(" - - - cols {}".format(gdf_CatUnificadoFilter.columns))
            departamento = gdf_CatUnificadoFilter["DEPARTAMENTO"].tolist()[0]
            municipio = gdf_CatUnificadoFilter["MUNICIPIO"].tolist()[0]
            id_predial = gdf_CatUnificadoFilter["id_predial"].tolist()[0]
            ced_cat = gdf_CatUnificadoFilter["numero_predial"].tolist()[0]
            ced_cat_ant = gdf_CatUnificadoFilter["numero_predial_anterior"].tolist()[0]
            direccion = gdf_CatUnificadoFilter["DIRECCION"].tolist()[0]
            clasifica_suelo_pot = gdf_CatUnificadoFilter["clasifica_suelo_pot"].tolist()[0]
            area_terreno_igac = gdf_CatUnificadoFilter["AREA TERRENO"].tolist()[0]
            area_construida = gdf_CatUnificadoFilter["AREA CONSTRUIDA"].tolist()[0]
            fmiCat = gdf_CatUnificadoFilter["MATRICULA INMOBILIARIA"].tolist()[0]
            area_geografica = gdf_CatUnificadoFilter["area_terreno_geografica"].tolist()[0]

            if not 'nan' in ced_cat:
                
                # Filtrando en SNR por FMI de catastro y por propietario
                df_snr_filterFMI = df_snr[df_snr["MATRICULA"] == fmiCat]
                df_snr_filter = df_snr_filterFMI[df_snr_filterFMI['PROPIETARIO'] == "X"]
                # orden descendente en ID ANOTACION
                df_snr_filter["ID ANOTACION"] = df_snr_filter["ID ANOTACION"].astype(int)
                df_snr_filter = df_snr_filter.sort_values(by='ID ANOTACION', ascending=False) 
                list_IDanotacion = df_snr_filter["ID ANOTACION"].tolist() #Lista de ID anotacion 
                list_DocsID_SNR = df_snr_filter["NRO DOCUMENTO"].tolist() #Lista Documentos de identidad SNR
                list_noms_SNR = df_snr_filter["NOMBRES"].tolist() #Lista Nombres SNR

                if(fmiCat == "" or fmiCat == "nan"):

                    interrelacionCatSNR = "1" #Interrelacion Catastro registro: Sin folio
                    ultimo_propietario_snr = ""
                    cedCat_fmi = ""
                    fmiActivo = ""
                    # Coincidencia Catastro Registro
                    coincidePropietario = "3" #Sin interrelación
                    propietarioCatastro = list_noms_Catastro[0] #Se toma cualquier nombre de la lista de catastro Unificado

                elif (fmiCat in snr_fmi_list):

                    interrelacionCatSNR = "2" #Interrelacion Catastro registro: interrelacion
                    cedCat_fmi = df_snr_filterFMI['NRO CATASTRO'].tolist()[0]
                    fmiEstado = df_snr_filterFMI['ESTADO ORIGEN'].tolist()[0]
                    fmiActivo = self.fmi_activo(fmiEstado)
                    if (len(list_IDanotacion)>0):
                        ultima_IDanotacion = list_IDanotacion[0]
                        df_snr_ultimoProp = df_snr_filter[df_snr_filter["ID ANOTACION"] == ultima_IDanotacion]
                        nombres_ultimoProp = df_snr_ultimoProp["NOMBRES"].tolist()
                        otro = self.y_otro(nombres_ultimoProp)
                        ultimo_propietario_snr = "{}{}".format(nombres_ultimoProp[0], otro)
                    else:
                        ultimo_propietario_snr = ""
                    propietarioCatastro, coincidePropietario, df_comparacion = self.compararPropietarioCatSnr(list_DocsID_Cat, list_DocsID_SNR, list_noms_Catastro, list_noms_SNR, list_IDanotacion, df_comparacion)

                else:

                    interrelacionCatSNR = "3" #Interrelacion Catastro registro: Solo en Catastro
                    ultimo_propietario_snr = ""
                    cedCat_fmi = ""
                    fmiActivo = ""
                    # Coincidencia Catastro Registro
                    coincidePropietario = "3" #Sin interrelación
                    propietarioCatastro = list_noms_Catastro[0] #Se toma cualquier nombre de la lista de catastro Unificado
                
                # Cuando hay más un propietario registrado en Catastro
                otro = self.y_otro(list_noms_Catastro)
                propietarioCatastro = "{}{}".format(propietarioCatastro, otro)

                #Aplicando función para categorizar el folio en sistema actual y antiguo
                circulo, folio, antiguo = self.separarFolio(fmiCat)

                row = {
                        "fmi":fmiCat, "id_predial": id_predial, "departamento": departamento,  
                        "municipio": municipio, "numero_predial": ced_cat,  
                        "numero_predial_anterior": ced_cat_ant, "circulo_registral": circulo, 
                        "numero_matricula": folio, "antiguo_sistema_registro": antiguo, 
                        "interrelacion_cat_reg": interrelacionCatSNR, "propietario_catastro": propietarioCatastro, 
                        "coincidencia_propietario": coincidePropietario,"area_terreno_r1": area_terreno_igac, 
                        "area_construida_r1":area_construida, 'area_terreno_geografica':area_geografica,
                        "clasificacion_suelo_pot": clasifica_suelo_pot, "ultimo_propietario_fmi": ultimo_propietario_snr, 
                        "direccion": direccion, "fmi_activo": fmiActivo, "cedula_catastral_fmi": cedCat_fmi
                    }
                df_api = df_api.append(row, ignore_index = True)
            else:
                pass
        
        return df_api, df_comparacion
    
    def Adicion_fmiSNR(self, df_api, snr_fmi_list, df_snr):
        """
            Función para adicionar folios de la SNR que no estan
            en Catastro Unificado
        """
        fmi_api_list = df_api["fmi"].tolist() #Folios existentes en df api
        
        for fmi_snr in snr_fmi_list:
            if fmi_snr in fmi_api_list:
                pass
            else:
                # Filtrando en SNR por FMI
                df_snr_filterFMI = df_snr[df_snr["MATRICULA"] == fmi_snr]
                df_snr_filter = df_snr_filterFMI[df_snr_filterFMI['PROPIETARIO'] == "X"]
                df_snr_filter["ID ANOTACION"] = df_snr_filter["ID ANOTACION"].astype(int)
                df_snr_filter = df_snr_filter.sort_values(by='ID ANOTACION', ascending=False)
                list_IDanotacion = df_snr_filter["ID ANOTACION"].tolist() #Lista de ID anotacion 
                interrelacionCatSNR = "0" #Interrelacion Catastro registro: Solo en SNR
                if (len(list_IDanotacion)>0):
                    ultima_IDanotacion = list_IDanotacion[0]
                    df_snr_ultimoProp = df_snr_filter[df_snr_filter["ID ANOTACION"] == ultima_IDanotacion]
                    nombres_ultimoProp = df_snr_ultimoProp["NOMBRES"].tolist()
                    otro = self.y_otro(nombres_ultimoProp)
                    ultimo_propietario_snr = "{}{}".format(nombres_ultimoProp[0], otro)
                else:
                    ultimo_propietario_snr = ""
                cedCat_fmi = df_snr_filterFMI['NRO CATASTRO'].tolist()[0]
                fmiEstado = df_snr_filterFMI['ESTADO ORIGEN'].tolist()[0]
                fmiActivo = self.fmi_activo(fmiEstado)
                # Coincidencia Catastro Registro
                coincidePropietario = "3" #Sin interrelación

                #Aplicando función para categorizar el folio en sistema actual y antiguo
                circulo, folio, antiguo = self.separarFolio(fmi_snr) 

                row = {
                    "fmi":fmi_snr, "circulo_registral": circulo, "numero_matricula": folio, 
                    "antiguo_sistema_registro": antiguo, "interrelacion_cat_reg": interrelacionCatSNR, 
                    "ultimo_propietario_fmi": ultimo_propietario_snr, "coincidencia_propietario": coincidePropietario, 
                    "fmi_activo": fmiActivo, "cedula_catastral_fmi": cedCat_fmi
                }
                df_api = df_api.append(row, ignore_index = True)
        
        return df_api
    
    def compararPropietarioCatSnr(self, list_DocsID_Cat, list_DocsID_SNR, list_noms_Catastro, list_noms_SNR, list_IDanotacion, df_comparacion):
        """
            Función para comparar la coincidencia del propietario en 
            catastro y en registro 
        """
        if (len(list_DocsID_SNR) > 0):
            # Comparación por documentos de identidad
            i = 0 # Contador para saber si coincide con propietario actual o anterior 
            for docIDsnr in list_DocsID_SNR:
                if (docIDsnr in list_DocsID_Cat):
                    indice = list_DocsID_Cat.index(docIDsnr) # indice en lista de documentos para obtener el nombre de Catastro
                    nombre_cat = list_noms_Catastro[indice]
                    comparacion = "IGUAL"
                    break
                else:
                    comparacion = "DIFERENTE"
                i += 1
            
            if(comparacion != "IGUAL"):
                # Comparación por nombres
                i = 0 # Contador para saber si coincide con propietario actual o anterior 
                for nombre_snr in list_noms_SNR: #Se recorre la lista nombres SNR ordenado por el id anotación (descente)
                    nombre_snr_normal = self.normalizar(nombre_snr)
                    for nombre_cat in list_noms_Catastro:
                        nombre_cat_normal = self.normalizar(nombre_cat)
                        comparacion, porcentaje = self.comparaNombres(nombre_snr_normal, nombre_cat_normal)
                        df_comparacion = df_comparacion.append({"Nombre SNR":nombre_snr_normal, "Nombre Catastro":nombre_cat_normal, "Porcentaje":porcentaje}, ignore_index = True)
                        if comparacion == "IGUAL": #Si coindicen que pare el bucle 
                            break
                    if comparacion == "IGUAL": #Si coindicen que pare el bucle
                        break
                    i += 1
            propietarioCatastro = nombre_cat
            
        else:

            propietarioCatastro = list_noms_Catastro[0]
            comparacion = ""
            
        # Determinando la coincidencia y nombre de propietario catastro
        if (comparacion == "IGUAL" and i == 0):
            coincidePropietario = "0" #Coincide con actual propietario
        elif(comparacion == "IGUAL" and i > 0):
            
            if (list_IDanotacion[0] == list_IDanotacion[i]): #Si hay más de un propietario con el mismo ID anotación
                coincidePropietario = "0" #Coincide con actual propietario
            else:
                coincidePropietario = "2" #Coincide con un propietario anterior

        else:
            coincidePropietario = "1" #No Coinciden
        
        return propietarioCatastro, coincidePropietario, df_comparacion

    
    def catastro_SNR(self, feedback, insumos, gdf_CatUnificado, output):
        """
            Función para cruzar catastro unificado y snr
        """
        #Leyendo Base Registral SNR
        pathSNR = insumos + "/Base Registral Snr.xlsx"
        
        feedback.pushInfo(" - 4.1 Leyendo Base Registral SNR")
        df_snr = pd.read_excel(pathSNR) #df de SNR
        
        #Quitando espacios y ceros a la izquierda
        feedback.pushInfo(" - 4.2 Normalizando campos")   
        
        #Normalizando 
        df_snr["MATRICULA"] = df_snr.apply(lambda x: self.quitarCeros(x["MATRICULA"]), axis=1)
        df_snr["MATRICULA"] = df_snr.apply(lambda x: self.normalizarFMI(x["MATRICULA"]), axis=1)
        df_snr["FOLIO DERIVADO"] = df_snr.apply(lambda x: self.quitarCeros(x["FOLIO DERIVADO"]), axis=1)
        df_snr["FOLIO DERIVADO"] = df_snr.apply(lambda x: self.normalizarFMI(x["FOLIO DERIVADO"]), axis=1)
        df_snr["NRO DOCUMENTO"] = df_snr.apply(lambda x: self.quitarCeros(x["NRO DOCUMENTO"]), axis=1)
        snr_fmi_list = df_snr["MATRICULA"].unique().tolist() #Lista de FMI en SNR

        feedback.pushInfo(" - 4.3 Obteniendo los valores unicos (CedulaCatastral-fmi) de Catastro unificado")
        gdf_CatUnificado["cedCat_fmi"] = gdf_CatUnificado.apply(lambda x: str(x["numero_predial"]) + "-" + str(x["MATRICULA INMOBILIARIA"]), axis =1)
        cedCat_fmi_list = gdf_CatUnificado["cedCat_fmi"].unique().tolist() #Lista de FMI en Catastro Unificado

        feedback.pushInfo(" - 4.4 Verificando interrelación catastro Registro")
        feedback.pushInfo("    - - 4.4.1 Folios de Catastro presentes en SNR (cedula_cat_fmi) - Coincidencia propietario")
        df_api1, df_comparacion = self.fmiCat_enSNR(cedCat_fmi_list, gdf_CatUnificado, snr_fmi_list, df_snr, feedback)

        feedback.pushInfo("    - - 4.4.2 Adicionando folios de SNR que no se relacionan con Catastro (tipo rural y sin info)")
        #Filtrando por tipo de predio RURAL Y SIN INFORMACIÓN
        df_snr_rural = df_snr[df_snr["TIPO PREDIO"] != "URBANO"]
        snr_fmi_list_rural = df_snr_rural["MATRICULA"].unique().tolist() #Lista de FMI en SNR
        df_api2 = self.Adicion_fmiSNR(df_api1, snr_fmi_list_rural, df_snr_rural)

        #Definiendo el nombre de departamento y municipio para todos los datos
        df_api2["departamento"] = df_api1["departamento"].tolist()[0]
        df_api2["municipio"] = df_api1["municipio"].tolist()[0]
        
        feedback.pushInfo(" - 4.5 Folios Matrices y Segregados")
        df_api2[['fmi_matriz', 'fmi_segregado']] = df_api2.apply(lambda x: self.encontrar_matriz_segregado(x["fmi"], df_snr), axis=1)
        del df_api2["fmi"] #Eliminando fmi

        # exportando resultado a excel
        feedback.pushInfo(" - - 4.6 exportando resultado a excel")
        xlsPath = output + "/api_preliminar.xlsx"
        df_api2.to_excel(xlsPath)

        # Exportando comparación de nombres a excel
        xlsPath = output + "/Comparacion_Nombres.xlsx"
        df_comparacion.to_excel(xlsPath)
        
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

        feedback.pushInfo("1. Cruce Base Catastral y Cartografía POT".upper())
        #Cruce Base Catastral y Cartografía POT Retorna un Geodataframe
        gdf_baseCPOT = self.baseCatastral_CartoPOT(feedback ,baseCatastral, cartoPOT, output)

        feedback.pushInfo("\n\n2. Cruce R1 y R2".upper())
        #Cruce R1 y R2 retorna un df
        df_r1r2 = self.r1_r2(insumos, feedback, output)

        feedback.pushInfo("\n\n3. Catastro Unificado: Base Carto POT y Unificado R1-R2".upper())
        gdf_CatUnificado = self.catastro_unificado(feedback, df_r1r2, gdf_baseCPOT, output)

        feedback.pushInfo("\n\n4. Catastro Unificado y SNR".upper())
        self.catastro_SNR(feedback, insumos, gdf_CatUnificado, output)

        feedback.pushInfo("\n\n#### ------  Analisis Predial Integral V.0 ------ ####\n\n")
        feedback.pushInfo("      ---------------------")
        feedback.pushInfo("      |-    By: ljimj    -|")
        feedback.pushInfo("      ---------------------")

                 
        return {}
