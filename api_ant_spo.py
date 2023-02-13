import pandas as pd
import psycopg2
import psycopg2.extras as extras
import numpy as np
from datetime import datetime
from fuzzywuzzy import fuzz
import csv


def execute_values(conn, df, table):
    """
        Función para guardar los datos procesados 
        en un dataframe de pandas en una tabla 
        de la base de datos postgres 
    """
  
    tuples = [tuple(x) for x in df.to_numpy()]
  
    cols = ','.join(list(df.columns))
  
    # SQL query to execute
    query = "INSERT INTO %s(%s) VALUES %%s" % (table, cols)
    cursor = conn.cursor()
    try:
        extras.execute_values(cursor, query, tuples)
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error: %s" % error)
        conn.rollback()
        cursor.close()
        return 1
    print("execute_values() done")
    cursor.close()


def natu_juridica(df_snr):
    """
        Función para determinar la naturaleza Jurídica de un predio
        de acuerdo a las anotaciones del folio y cruces con catastro
    """
    # 1 PREDIO CON TITULOS DE TRADICIÓN
    # ID NATURALEZA JURIDICA
    # títulos originarios del Estado, identificado con los siguientes códigos (en cualquiera de sus anotaciones): 103, 104, 105, 106, 116
    buscar = ['103', '104', '105', '106', '116', ]


def encontrar_matriz_segregado(fmi, df_snr):
    """
        Función para encontrar los folios matriz y segregados
    """

    fmiListM = df_snr['MATRICULA'].tolist() #Lista de todos los FMI existentes en SNR
    if(fmi in fmiListM): #si el fmi se encuentra en la lista continue

        #Operaciones para determinar los fmi derivados
        df_snr_filterS = df_snr[df_snr['MATRICULA'] == fmi] #Filtro para encontrar segregados del fmi
        list_snrS = set(df_snr_filterS['FOLIO DERIVADO'].tolist()) #Lista de segregados unicos
        segregados = ""
        for segre in list_snrS:
            if "-" in segre:
                segre = "0{}".format(segre)
            segregados += "{};".format(segre)
    else:
        segregados = ""
    
    fmiListD = df_snr['FOLIO DERIVADO'].tolist()
    if(fmi in fmiListD):
        #Operaciones para determinar los fmi matrices
        df_snr_filterM = df_snr[df_snr['FOLIO DERIVADO'] == fmi] #Filtro para encontrar matrices del fmi
        list_snrM = set(df_snr_filterM['MATRICULA'].tolist()) #Lista de Matrices
        matrices = ""
        for matri in list_snrM:
            if "-" in matri:
                matri = "0{}".format(matri)
            matrices += "{};".format(matri)
            
    else:
        matrices = ""

    reemplazar = (("nan",""),(";;",""))
    for a, b in reemplazar:
        segregados = segregados.replace(a, b)
        matrices = matrices.replace(a, b)
        try:
            if (segregados[0] == ";"):
                segregados = segregados[1:]
        except:
            pass
        try:
            if (matrices[0] == ";"):
                matrices = matrices[1:]
        except:
            pass
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


    return matrices, segregados


def separarFolio(fmi):
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
    return pd.Series([circulo, folio, antiguo])



def comparaNombres(nombre1, nombre2):
    """
        Función para comparar dos nombres
        Si no son exactamente iguales se va establecer
        en qué porcentaje son iguales.
        Si el nombre1 <= 0.15 desigual al nombre2 Retorna "IGUAL"
    """
    porcentaje = fuzz.ratio(nombre1,nombre2) 
    # Función para comparar palabras retornando un porcentaje 0%-100% de similitud
    if porcentaje >= 80:
        comparacion = "IGUAL"
    else:
        comparacion = "DESIGUAL"

    return comparacion, porcentaje
        
        

def normalizar(nombre):
    """
        Función para normalizar nombres buscando y reemplazando
        los caracteres descritos
    """
    reemplazos = ( #(Buscar, reemplazar)
        ("á", "a"), ("é", "e"), ("í", "i"), ("ó", "o"), ("ú", "u"), (".", ""),(" y ", " "),
        ("-", ""), ("_", ""), ("*", ""), ("+", ""), ("&", ""), ("'", ""), ('"', ''),
        ("ñ", "n"), ("sucesores", ""), ("sucesor", ""), (" su ", " "), (" suc ", " "), 
        (" del ", " "), ('de los', ' '), ("de la", " "), ("de las", " "), (" de ", " "),
        ("vda de", ""), ('vda', ''), (" cia", ""), ("ltda", "")
    )
    nombre = nombre.lower() # pasando el nombre a minusculas
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

def quitarCerosDocID(docID): 
    """
        Función para normalizar el documento
        de identidad (quitar ceros)
    """
    docID = str(docID) # pasando documento a string
    docID = docID.strip() #Quitando posibles espacios
    i = 0 #Inicializando Contador de ceros 
    docIDnorm = str() #Definiendo el docID como string
    for doc in docID:
        #Ciclo para recorrer cada caracter el numero
        if (doc == "0"):
            #Si es cero que lo cuente
            i += 1
        else:
            # Si no es cero es porque es el inicio del número
            # Romper ciclo for
            docIDnorm = docID[i:] #Tomar el docID despues del caracter i (izquierda(i))
            break
    
    return docIDnorm
        

def compararPropietarioCatSnr(df_r1, df_r2, df_snr, fmi, cedCat, interCatReg, writer):
    """
        Función para comparar la coincidencia del propietario en 
        catastro (r1-r2) y en registro (snr)
    """
    
    if (interCatReg == 2): # se realiza la busqueda a los que tienen interrelación catastro registro
        
        #Obteniendo información de Reg1 y Reg2 de acuerdo al fmi
        fmiList = df_r2['MATRICULA INMOBILIARIA'].tolist()
        if(fmi in fmiList):

            df_r1_filter = df_r1[df_r1['Cedula Castastral 30'] == cedCat]
            nombreCatastro = normalizar(df_r1_filter['NOMBRE'].tolist()[0])
            docIDCatastro = quitarCerosDocID(df_r1_filter['NUMERO DOCUMENTO'].tolist()[0])

            #Operaciones con SNR de acuerdo al fmi, nombre_catastro y docID_catastro
            df_snr_filter1 = df_snr[df_snr['MATRICULA'] == fmi]
            df_snr_filter2 = df_snr_filter1[df_snr_filter1['PROPIETARIO'] == "X"]
            df_snr_filter2['ID ANOTACION'] = pd.to_numeric(df_snr_filter2['ID ANOTACION'])
            df_snr_filter2.sort_values(by='ID ANOTACION', inplace = True)

            docIDSNR = df_snr_filter2["NRO DOCUMENTO"].tolist()
            nombresSNR = df_snr_filter2["NOMBRES"].tolist()
            if(len(nombresSNR)>0):
                ultimo_propSNR = nombresSNR[-1]
            else:
                ultimo_propSNR = ""
            #print("{}".format(docIDCatastro))
            if(docIDCatastro in docIDSNR):
                # Comparación por números de documento de identidad
                #print("DocID - {} - {}".format(fmi, cedCat))
                if(docIDSNR[-1] == docIDCatastro):
                    coincidencia = 0
                else:
                    coincidencia = 2
            else:
                #Comparación con nombres
                i = 0
                lenlistNom = len(nombresSNR) #Cantidad de nombres (propietario) encontrados por el folio 
                compara = list()
                for nombreSNR in nombresSNR:
                    nombreSNR = normalizar(nombreSNR)
                    comparacion, porcentaje = comparaNombres(nombreCatastro, nombreSNR)
                    writer.writerow([fmi, cedCat, nombreCatastro, nombreSNR, porcentaje])
                    if(comparacion == "IGUAL"):
                        if(i == lenlistNom-1):
                            compara.append(0)
                        else:
                            compara.append(2)
                    else:
                        compara.append(1)
                
                if (0 in compara):
                    coincidencia = 0
                elif (2 in compara):
                    coincidencia = 2
                else:
                    coincidencia = 1
        else:
            coincidencia = 1
            ultimo_propSNR = ""
    else: # Si no tiene interrelación catastro registro que retorne "3: Sin interrelación"
        coincidencia = 3
        ultimo_propSNR = ""
    
    return coincidencia, ultimo_propSNR

def funCentral (df_r1, df_r2, df_snr, fmi, cedCat, interCatReg, writer):
    """
        Función central para evaluar otras funciones
    """
    coincidencia, ultimo_propSNR = compararPropietarioCatSnr(df_r1, df_r2, df_snr, fmi, cedCat, interCatReg, writer)
    matrices, segregados = encontrar_matriz_segregado(fmi, df_snr)

    return pd.Series([coincidencia, ultimo_propSNR, matrices, segregados])

# Data frame Pandas de la Base registral

df_snr = pd.read_excel(r'C:\Users\LEO_J\Desktop\ANT-SPO\Automatizacion API\Insumos-prueba\insumos\Base Registral Snr.xlsx')
print("\nLeyendo SNR")
df_snr["MATRICULA"]= df_snr.apply(lambda x: quitarCerosDocID(x["MATRICULA"]), axis=1)
df_snr["MATRICULA"] = df_snr["MATRICULA"].str.strip()
df_snr["FOLIO DERIVADO"]= df_snr.apply(lambda x: quitarCerosDocID(x["FOLIO DERIVADO"]), axis=1)
df_snr["FOLIO DERIVADO"] = df_snr["FOLIO DERIVADO"].str.strip()
#print(df_snr.columns.values)


# Data frame Pandas de la Registro 1
df_r1 = pd.read_excel(r'C:\Users\LEO_J\Desktop\ANT-SPO\Automatizacion API\Insumos-prueba\insumos\Registro 1 Igac Detalle.xlsx')
print("\nLeyendo R1")

#print(df_r1.columns.values)
# Data frame Pandas de la Base registral
df_r2 = pd.read_excel(r'C:\Users\LEO_J\Desktop\ANT-SPO\Automatizacion API\Insumos-prueba\insumos\Registro 2 Igac Detalle.xlsx')
print("\nLeyendo R2")
df_r2["MATRICULA INMOBILIARIA"] = df_r2.apply(lambda x: quitarCerosDocID(x["MATRICULA INMOBILIARIA"]), axis=1)
df_r2["MATRICULA INMOBILIARIA"] = df_r2["MATRICULA INMOBILIARIA"].str.strip()
#print(df_r2.columns.values)

# Dataframe ReporteAPI_SAN JACINTO
df_SanJac = pd.read_excel(r'C:\Users\LEO_J\Desktop\ANT-SPO\Automatizacion API\Insumos-prueba\insumos\ReporteAPI_SAN JACINTO.xlsx')
print("\nLeyendo San Jacinto")
print(len(df_SanJac.index))
print(len(df_SanJac["FMI_SNR"].index))
df_SanJac["FMI_SNR"] = df_SanJac["FMI_SNR"].str.strip()
df_SanJac[["circulo", "folio", "antiguo"]] = df_SanJac.apply(lambda x: separarFolio(x["FMI_SNR"]), axis=1)
df_SanJac["FMI_SNR"] = df_SanJac.apply(lambda x: quitarCerosDocID(x["FMI_SNR"]), axis=1)
df_SanJac["FMI_SNR"] = df_SanJac["FMI_SNR"].str.strip()

#print(df_SanJac.columns.values)
with open(r'C:\Users\LEO_J\Desktop\ANT-SPO\Automatizacion API\Desarrollos\nombres.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["fmi","cedCat","Cat","Reg","%"])
    df_SanJac[['coincidencia_propietario', 'ultimo_propSNR', 'matriz', 'segregado']] = df_SanJac.apply(lambda x: funCentral(df_r1, df_r2, df_snr , x["FMI_SNR"], x["CEDULA_CATASTRAL_NUEVO"], x["INTERRELACION_CATASTRO_REGISTRO"], writer), axis=1)

df_api = pd.DataFrame(columns = [
    #Campos de la base de datos API
   'id_barrido_ant', 'departamento', 'municipio',
   'circulo_registral', 'numero_matricula', 'antiguo_sistema_registro',
   'numero_predial', 'numero_predial_anterior', 'interrelacion_cat_reg',
   'clasificacion_suelo_igac', 'clasificacion_suelo_pot', 'codigo_vereda_catastral',
   'vereda_dane', 'div_politico_admin_pot', 'unidad_intervencion_pospr',
   'id_parcel', 'nombre_predio_snr', 'nombre_predio_catastro',
   'naturaleza_predio', 'relacion_tenencia', 'objeto_de_ospr',
   'area_terreno_r1', 'area_terreno_geografica', 'area_snr',
   'cruza_determinantes_ospr', 'alcance_determinantes', 'Área_habilitada_para_ospr',
   'oferta_agrolÓgica', 'area_construida_r1', 'mejora_predio_ajeno',
   'numero_mejoras', 'presunto_baldio_t488', 'situacion_limite_municipal',
   'departamento_limite_municipal', 'municipio_limite_municipal', 'area_predio_excede_limite',
   'propietario_catastro', 'ultimo_propietario_fmi', 'coincidencia_propietario',
   'cedula_catastral_fmi', 'fmi_activo', 'fmi_matriz', 'fmi_matriz_activo',
   'fmi_segregado', 'proceso_urt', 'inscripcion_rupta', 'posible_cultivo_ilicito',
   'fmi_adjud_incora_incoder', 'predio_comprado_fna']
)

#Tomando datos

df_api['departamento'] = df_SanJac['DEPARTAMENTO']
df_api['municipio'] = df_SanJac['MUNICIPIO']
df_api['coincidencia_propietario'] = df_SanJac['coincidencia_propietario']
df_api['circulo_registral'] = df_SanJac['circulo'].str[:4]
df_api['numero_matricula'] = df_SanJac['folio']
df_api['antiguo_sistema_registro'] = df_SanJac['antiguo']

df_api['numero_predial'] = df_SanJac['CEDULA_CATASTRAL_NUEVO']
df_api['numero_predial_anterior'] = df_SanJac['CEDULA_CATASTRAL_ANTIGUO'].str[:20]
df_api['interrelacion_cat_reg'] = pd.to_numeric(df_SanJac['INTERRELACION_CATASTRO_REGISTRO'])
df_api['propietario_catastro'] = df_SanJac['PROPIETARIO_CATASTRO']
df_api['clasificacion_suelo_igac'] = df_SanJac['CLASIFICACION_CATASTRAL']
df_api['presunto_baldio_t488'] = df_SanJac['PRESUNTO_BALDIO_T488']
df_api['ultimo_propietario_fmi'] = df_SanJac['ultimo_propSNR']
df_api['fmi_matriz'] = df_SanJac['matriz'].str[:255]
df_api['fmi_segregado'] = df_SanJac['segregado'].str[:255]
df_api = df_api.replace({np.nan: None})

#print("\n\n")
#print(df_api.head())


#Conexion a bd
conn = psycopg2.connect(
   database = 'ant_spo', user = 'postgres', password = "LEO2021", host = 'localhost', port = '5432'
)

cursor = conn.cursor()

cursor.execute('''TRUNCATE TABLE api.analisis_predial_integral''')

conn.commit()

execute_values(conn, df_api, 'api.analisis_predial_integral')
conn.commit()

print('\n\n\n ## --> Finalizado <--##')