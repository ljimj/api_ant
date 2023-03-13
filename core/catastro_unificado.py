import pandas as pd
import geopandas as gpd
from core.fun_generales import *

def catastro_unificado(feedback, df_r1r2, gdf_baseCPOT, output):
    """
        Función para realizar cruce por cedula catastral entre 
        la base catastral POT y la unificada de los registros 1 y 2
    """
    # Creando un dataframe donde se almacenaran la unión
    feedback.pushInfo(" - 3.1 Cruzando por Cedula Catastral (30 dig)")
    gdf_CatUnificado = gdf_baseCPOT[["id_predial", "numero_predial", "clasifica_suelo_pot", "area_terreno_geografica", "geom"]].merge(df_r1r2[["DEPARTAMENTO", "MUNICIPIO", "MATRICULA INMOBILIARIA", "NUMERO DE PREDIO", "numero_predial_anterior","numero_predial", "NOMBRE", "NUMERO DOCUMENTO", "DIRECCION", "AREA TERRENO", "AREA CONSTRUIDA"]], on = "numero_predial", how = "outer")

    feedback.pushInfo(" - 3.2 Quitando ceros y duplicados (CedulaCatastral-FMI-Nombre)")
    gdf_CatUnificado["numero_predial"] = gdf_CatUnificado.apply(lambda x: quitar_ceros(x["numero_predial"]), axis=1)
    gdf_CatUnificado["MATRICULA INMOBILIARIA"] = gdf_CatUnificado.apply(lambda x: quitar_ceros(x["MATRICULA INMOBILIARIA"]), axis=1)
    gdf_CatUnificado["MATRICULA INMOBILIARIA"] = gdf_CatUnificado.apply(lambda x: normalizar_fmi(x["MATRICULA INMOBILIARIA"]), axis=1)
    gdf_CatUnificado["NUMERO DOCUMENTO"] = gdf_CatUnificado.apply(lambda x: quitar_ceros(x["NUMERO DOCUMENTO"]), axis=1)
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