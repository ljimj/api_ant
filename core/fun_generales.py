import pandas as pd
from fuzzywuzzy import fuzz

def y_otro(list_nombres):
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

def fmi_activo(estado):
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

def normalizar(nombre):
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

def encontrar_matriz_segregado(fmi, urbano, df_snr, fmiListM, fmiListD):
    """
        Función para encontrar los folios matriz y segregados
    """
    if(fmi != "" and urbano == "NO"):

        #SEGREGADOS
        
        if(fmiListM == fmi).any(): #si el fmi se encuentra en la lista continue

            #Operaciones para determinar los fmi derivados
            df_snr_filterS = df_snr[df_snr['MATRICULA'] == fmi] #Filtro para encontrar segregados del fmi
            list_snrS = df_snr_filterS['FOLIO DERIVADO'].unique() #Lista de segregados unicos
            segregados = list()
            for segre in list_snrS:
                if(segre != "" and segre != "nan" and segre != None):
                    segregados.append(segre)
            segregados = ";".join(segregados)
        else:
            segregados = ""
                    
        if(fmiListD == fmi).any():
            #Operaciones para determinar los fmi matrices
            df_snr_filterM = df_snr[df_snr['FOLIO DERIVADO'] == fmi] #Filtro para encontrar matrices del fmi
            list_snrM = df_snr_filterM['MATRICULA'].unique() #Lista de Matrices
            matrices = list()
            for matri in list_snrM:
                if(matri != "" and matri != "nan" and matri != None):
                    matrices.append(matri)
            matrices= ";".join(matrices)
        else:
            matrices = ""
    else:
        matrices = "" 
        segregados = ""

    return pd.Series([matrices, segregados])

def separar_folio(fmi):
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
    elif(str(fmi) == "" or str(fmi) == "nan" or str(fmi) == None):
        circulo = ""
        folio = ""
        antiguo = ""
    else: # Si no que el circulo este vacio y el folio igual fmi
        circulo = ""
        folio = ""
        antiguo = fmi
    #print("{} / {}".format(circulo, folio))
    return circulo, folio, antiguo

def normalizar_fmi(fmi):
    """
        Función para normalizar los folios de matricula

    """
    fmi = str(fmi)
    guiones = fmi.count("-")
    if fmi == "nan" or fmi == None:
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

def compara_nombres(nombre1, nombre2):
    """
        Función para comparar dos nombres
        Si no son exactamente iguales se va establecer
        en qué porcentaje son iguales.
        Si son iguales en un >83% Retorna "IGUAL"
    """
    if (nombre1 != "" or nombre2 != "" or nombre1 != "nan" or nombre2 != "nan" or nombre1 != None or nombre2 != None):

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
    
def quitar_ceros(num): 
    """
        Función para normalizar el documento
        de identidad (quitar ceros)
    """
    num = str(num) # pasando documento a string
    num = num.strip() #Quitando posibles espacios
    numNorm = num.lstrip('+-0') #Quitando ceros a la izquierda
    
    return numNorm