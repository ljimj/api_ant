import pandas as pd
from reglas_cod_reg import *
from condiciones_query import condiciones_dict

def condiciones_generales(fmi, fmi_matriz, fmi_segregado, df_snr):
    """
        Función para evaluar las condiciones generales
    """
    print(f"fmi: {fmi} matriz {fmi_matriz}")
    # Extrayendo las condiciones
    condiciones = condiciones_dict()

    # definiendo tipo de dato para Id anotación y fecha radicación
    df_snr['ID ANOTACION'] = df_snr['ID ANOTACION'].astype(int)
    df_snr = df_snr.sort_values(by='ID ANOTACION', ascending=False)
    df_snr['FECHA RADICACION'] = pd.to_datetime(df_snr['FECHA RADICACION'], format='%d/%m/%Y')

    #Filtrando por fmi
    df_snrFMI = df_snr[df_snr['MATRICULA'] == fmi]

    naturaleza = ""
    rel_tenencia = "" 
    objetoOSPR = ""
    fmi_adjud_incora_incoder = ""
    # Regla 1 PREDIO CON TITULOS DE TRADICIÓN
    naturaleza, fmi_adjud_incora_incoder = condicion_general_r1r12(df_snrFMI, condiciones["r1p1"])
    if (naturaleza == ""):
        #regla 2 y 3 PREDIO CON TITULOS DE TRADICIÓN y PREDIO CON POSESIONES O FALSA TRADICIONES EN FOLIO
        naturaleza, rel_tenencia, objetoOSPR = condicion_general_r2_r3(df_snrFMI)
    if (naturaleza == ""):
        # Regla 4
        naturaleza, rel_tenencia, objetoOSPR = condicion_general_r4(df_snrFMI, fmi_matriz, df_snr)
    if (naturaleza == ""):
        # Regla 5 PREDIO CON POSESIONES O FALSA TRADICIONES EN FOLIO
        naturaleza, rel_tenencia, objetoOSPR = condicion_general_r5(df_snrFMI, fmi_matriz, df_snr)
    if (naturaleza == ""):
        # Regla 7 PREDIOS CON GRAVAMENES - HIPOTECA
        naturaleza, rel_tenencia, objetoOSPR = condicion_general_r7tor14(df_snrFMI, fmi_matriz, df_snr, condiciones["r7p1"])
    if (naturaleza == ""):
        # Regla 8 PREDIO CON AFECTACIONES- LIMITACIÓN 
        naturaleza, rel_tenencia, objetoOSPR = condicion_general_r7tor14(df_snrFMI, fmi_matriz, df_snr, condiciones["r8p1"])
    if (naturaleza == ""):
        # Regla 9 PREDIO CON SERVIDUMBRES 
        naturaleza, rel_tenencia, objetoOSPR = condicion_general_r7tor14(df_snrFMI, fmi_matriz, df_snr, condiciones["r9p1"])
    if (naturaleza == ""):
        # Regla 10 PREDIOS CON ENGLOBE, DESENGLOBE, LOTEO
        naturaleza, rel_tenencia, objetoOSPR = condicion_general_r7tor14(df_snrFMI, fmi_matriz, df_snr, condiciones["r10p1"])
    if (naturaleza == ""):
        # Regla 11 PREDIOS CON ACLARACIONES, CORRECIONES Y ACTUALIZACIONES
        naturaleza, rel_tenencia, objetoOSPR = condicion_general_r7tor14(df_snrFMI, fmi_matriz, df_snr, condiciones["r11p1"])
    if (naturaleza == ""):
        # Regla 12 PREDIO CON TITULOS DENOMINADOS "OTROS"
        naturaleza, fmi_adjud_incora_incoder = condicion_general_r1r12(df_snrFMI, condiciones["r12p1"])
    if (naturaleza == ""):
        # Regla 13 PREDIOS CON MEDIDAS CAUTELARES 
        naturaleza, rel_tenencia, objetoOSPR = condicion_general_r7tor14(df_snrFMI, fmi_matriz, df_snr, condiciones["r13p1"])
    if (naturaleza == ""):
        # Regla 14 PREDIOS CON CANCELACIONES 
        naturaleza, rel_tenencia, objetoOSPR = condicion_general_r7tor14(df_snrFMI, fmi_matriz, df_snr, condiciones["r14p1"])

    return naturaleza, fmi_adjud_incora_incoder, rel_tenencia, objetoOSPR

  
def codRegistrales(numero_predial, fmi, fmi_antiguio, interrelacion, urbano, fmi_matriz, fmi_segregado, dfCunificado, df_snr):
    """
        Función para analizar por folio y por codigos registrales,
        asi poder determinar la naturaleza jurídica, relación tenencia 
        entre otros
    """
    #Llamando las condiciones
    condiciones = condiciones_dict()

    naturaleza = ""
    rel_tenencia = ""
    objetoOSPR = ""
    fmi_adjud_incora_incoder = ""
    #Folios antiguos
    if len(str(fmi_antiguio)) == 18 and fmi_antiguio[0] == "1":
        naturaleza = "Privado" # Privado
        rel_tenencia = "Poseedor"
        objetoOSPR = "Formalizacion"
    # Folios solo en catastro o sin Folio
    elif interrelacion in ("1","3"):
        condiciones = condiciones["nacion_similares"]
        naturaleza, rel_tenencia, objetoOSPR = nacion_similares(numero_predial, dfCunificado, condiciones)
        if(naturaleza == ""):
            naturaleza = "Publico - Baldio"
            rel_tenencia = "Ocupante"
            objetoOSPR = "Acceso a tierras"
    else:
        if urbano != "SI":
            naturaleza, fmi_adjud_incora_incoder, rel_tenencia, objetoOSPR = condiciones_generales(fmi, fmi_matriz, fmi_segregado, df_snr)
        

    return pd.Series([naturaleza, rel_tenencia, objetoOSPR, fmi_adjud_incora_incoder])


path_api = r"C:\Users\LEO_J\Desktop\ANT-SPO\Automatizacion API\Pruebas_Salida_SJ\api_preliminar.xlsx"
api_preliminar = pd.read_excel(path_api, dtype=str)
api_preliminar = api_preliminar.fillna("")
api_preliminar = api_preliminar.replace(to_replace="nan",value="")

pathCunificado = r"C:\Users\LEO_J\Desktop\ANT-SPO\Automatizacion API\Insumos-prueba\insumos\CatastroUnificado_Registros_CartoBase_POT.csv"
gdf_CatUnificado = pd.read_csv(pathCunificado, dtype=str, engine='python')
gdf_CatUnificado = gdf_CatUnificado.fillna("")
gdf_CatUnificado = gdf_CatUnificado.replace(to_replace="nan",value="")
dfCunificado = gdf_CatUnificado[['numero_predial','MATRICULA INMOBILIARIA', 'NOMBRE']]

path_snr = r"C:\Users\LEO_J\Desktop\ANT-SPO\Automatizacion API\Insumos-prueba\insumos\Base Registral Snr.csv"
df_snr = pd.read_csv(path_snr, dtype=str)
df_snr = df_snr.fillna("")
df_snr = df_snr.replace(to_replace="nan",value="")
print(df_snr.columns)
df_snr = df_snr[['MATRICULA', 'ID ANOTACION', 'ESPECIFICACION', 'FECHA RADICACION', 'COMPLEMENTACION', 'FOLIO DERIVADO']]
"""
    'ID', 'MATRICULA', 'COD DEPARTAMENTO', 'COD MUNICIPIO', 'DEPARTAMENTO',
       'MUNICIPIO', 'TIPO PREDIO', 'ID ANOTACION',
       'NATURALEZA JURIDICA COMPLETO', 'REQUIERE TRANSFORMACION NJ',
       'ID NATURALEZA JURIDICA', 'ESPECIFICACION', 'DOCUMENTO COMPLETO',
       'REQUIERE TRANSFORMACION DOC', 'TPDC NOMBRE', 'DOC NUMERO', 'DOC FECHA',
       'ROL PERSONA', 'TIPO DOCUMENTO', 'NRO DOCUMENTO', 'NOMBRES',
       'PROPIETARIO', 'NROCATASTRO', 'NRO CATASTRO ANT', 'ESTADO_FOLIO',
       'ESTADO', 'DIRECCION', 'FECHA RADICACION', 'CABIDA LINDEROS',
       'COMPLEMENTACION', 'FOLIO DERIVADO', 'FOLIO MATRIZ', 'Tipo Archivo',
       'Ruta', 'Nombre Archivo', 'Ruta Completa', 'Fecha Cargue',
       'Fecha Modificacion'
"""
#print(api_preliminar['antiguo_sistema_registro'])
api_preliminar[["naturaleza_predio", "relacion_tenencia", "objeto de ospr", "fmi_adjud_incora_incoder"]] = api_preliminar.apply(lambda x: codRegistrales(x['numero_predial'], x['fmi'], x['antiguo_sistema_registro'], x["interrelacion_cat_reg"], x["urbano"], x['fmi_matriz'], x['fmi_segregado'], dfCunificado, df_snr), axis=1)
api_preliminar = api_preliminar.loc[:,~api_preliminar.columns.str.match("Unnamed")]
ouput = r"C:\Users\LEO_J\Desktop\ANT-SPO\Automatizacion API\Pruebas_Salida_SJ\api_preliminarCodReg.xlsx"
api_preliminar.to_excel(ouput)