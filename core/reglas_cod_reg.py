from condiciones_query import condiciones_dict
from fun_generales import encontrar_matriz_segregado

def nacion_similares(numero_predial, dfCunificado, patrones):
    """
        Función para determinar identificar en propietario palabras asociadas a la nación 
        o similares predios con folio SOLO ESTÁ EN CATASTRO o SIN FOLIO 
    """
    dfCunificado = dfCunificado[dfCunificado["numero_predial"] == numero_predial]
    naturaleza = "" 
    rel_tenencia = ""
    objetoOSPR = ""
    for patron in patrones:
        dfquery = dfCunificado.query(str(patron), engine='python')
        if len(dfquery)>0:
            naturaleza = "Publico - Baldio" # Publico - Baldio
            rel_tenencia = "Propietario" #Propietario
            objetoOSPR = ""
            break
    return naturaleza, rel_tenencia, objetoOSPR

def paso2_r1_r2(df_snr):
    """
        Función para comprobar si la regla 1 o 2
        cumplen con las condiciones del paso 2
    """
    # Extrayendo las condiciones
    condiciones = condiciones_dict()
    condicionesR1P2 = condiciones["r1p2"]
    r1r2p2 = ""
    for condi in condicionesR1P2:
        dfquery = df_snr.query(str(condi), engine='python')
        if len(dfquery)>0:
            r1r2p2 = "SI"
            break
    
    return r1r2p2

def paso2_r3(df_snr):
    """
        Función para comprobar si la regla 3
        cumplen con las condiciones del paso 2
    """
    # Extrayendo las condiciones
    condiciones = condiciones_dict()
    condicionesR3P2 = condiciones["r3p2"]
    naturaleza = ""
    rel_tenencia = ""
    objetoOSPR = ""
    for condi in condicionesR3P2:
        dfquery = df_snr.query(str(condi), engine='python')
        if len(dfquery)>0:
            naturaleza = "Privado - Posesión determinada en FMI"
            rel_tenencia = "Poseedor"
            objetoOSPR = "Formalización"
            break
    
    return naturaleza, rel_tenencia, objetoOSPR


def condicion_general_r1r12(df_snr, condiciones):
    """
        Función para comprobar si las anotaciones del folio
        cumplen con las condiciones de la regla 1 y regla 12
    """
    
    naturaleza = ""
    fmi_adjud_incora_incoder = ""

    for condi in condiciones:
        dfquery = df_snr.query(str(condi), engine='python')
        if len(dfquery)>0:
            idanotacion = int(dfquery['ID ANOTACION'].values[0])
            df_snrQuery = df_snr.loc[df_snr['ID ANOTACION'] > idanotacion]
            r1r2p2 = paso2_r1_r2(df_snrQuery)
            if r1r2p2 == "SI":
                naturaleza = "Fiscal Patrimonial"
            else:
                naturaleza = "Privado"
                fmi_adjud_incora_incoder = "SI"
            break

    return naturaleza, fmi_adjud_incora_incoder

def condicion_general_r2_r3(df_snr):
    """
        Función para comprobar si las anotaciones del folio
        cumplen con las condiciones de la regla 1
    """
    # Extrayendo las condiciones
    condiciones = condiciones_dict()
    condicionesR2R3P1 = condiciones["r2p1"]

    naturaleza = ""
    rel_tenencia = ""
    objetoOSPR = ""

    #Filtrando por anotaciones menores al 05/08/1974
    df_snrQuery = df_snr.loc[(df_snr["FECHA RADICACION"] < '05/08/1974') & (df_snr['ID ANOTACION'] == 1)]

    if len(df_snrQuery)>0:

        for condi in condicionesR2R3P1:
            dfquery = df_snrQuery.query(str(condi), engine='python')
            if len(dfquery)>0:
                df_snr = df_snr.loc[df_snr["ID ANOTACION"] > 1]
                r1r2p2 = paso2_r1_r2(df_snr)
                if r1r2p2 != "SI":
                    naturaleza, rel_tenencia, objetoOSPR = paso2_r3(df_snr)
                    if naturaleza == "":
                        naturaleza = "Privado"
                elif (r1r2p2 == "SI"):
                    naturaleza = "Fiscal Patrimonial"
                else:
                    naturaleza = "Privado"
                break

    return naturaleza, rel_tenencia, objetoOSPR

def paso2_r4_c1 (df_snr):
    """
        Función para comprobar si las complementaciones del folio
        cumplen con el paso 2 de la regla 4 condición 1
    """
    # Extrayendo las condiciones
    condiciones = condiciones_dict()
    condicionesR4P2C1 = condiciones["r4p2c1"]
    condicion1 = ""
    for condi in condicionesR4P2C1:
        dfquery = df_snr.query(str(condi), engine='python')
        if len(dfquery)>0:
            condicion1 = "SI"
            break
    
    return condicion1

def paso2_r4_c2 (df_snr, fmi_matriz):
    """
        Función para comprobar si cumplen con el paso 2 
        de la regla 4 condición 2 (folios matrices)
    """
    # Extrayendo las condiciones
    condiciones = condiciones_dict()
    condicionesR2P1 = condiciones["r2p1"]
    condicionesR4P2C1 = condiciones["r4p2c1"] #Complementaciones

    cumple = list() #Si cumple alguna de las condiciones
    matrices = fmi_matriz.split(";") #Matrices
    if len(matrices) > 0:
        for matriz in matrices:

            df_snrFMImatriz = df_snr.loc[df_snr["MATRICULA"] == matriz] #Filtrando por el matriz
            df_snrFMIm = df_snr.loc[df_snr["FECHA RADICACION"] < '05/08/1974'] #Filtrando menores a 5/8/1974

            if len(df_snrFMIm) > 0:
                #  códigos que transfieren dominio
                for condi in condicionesR2P1:
                    dfquery = df_snrFMIm.query(str(condi), engine='python')
                    if len(dfquery)>0:
                        cumple.append("SI")
                        break
            
            if not "SI" in cumple and len(df_snrFMImatriz) > 0:
                # COMPLEMENTACIONES del FMI 
                for condi in condicionesR4P2C1:
                    dfquery = df_snrFMImatriz.query(str(condi), engine='python')
                    if len(dfquery)>0:
                        cumple.append("SI")
                        break
        #Si no se cumple la CONDICION 1, 2 y 3 en el FMI matriz, 
        # se deben revisar las mismas 3 condiciones en el folio matriz de matriz 
        # y así sucesivamente.
        if not "SI" in cumple:
            # Encontrando folios matrices
            matrices_matrices = list()
            fmiListM = df_snr['MATRICULA'].unique() #Lista de todos los FMI existentes en SNR
            fmiListD = df_snr['FOLIO DERIVADO'].unique() #Lista de todos los FMI derivados existentes en SNR

            for matriz in matrices:
                matriz_segre = encontrar_matriz_segregado(matriz, "NO", df_snr, fmiListM, fmiListD)
                if matriz_segre[0] != "":
                    matrices_matrices.append(matriz_segre[0]) #Asignando matrices
            matrices_matrices = ";".join(matrices_matrices)
            if len(matrices_matrices) > 0:
                #Aplicando la función para evaluar los folio matrices
                naturaleza = paso2_r4_c2 (df_snr, matrices_matrices)
            else:
                naturaleza = "Baldio"

        else:    
            # En caso de contar con mas de un FMI matriz, 
            # donde se lleguen a conclusiones diferentes 
            # (uno me lleva a la conclusión de naturaleza privada y el otro de naturaleza baldía) 
            # PRIMA LA NATURALEZA BALDIA
            if len(cumple) == len(matrices):
                naturaleza = "Privado"
            else:
                naturaleza = "Baldio"
    else:
        naturaleza = "Baldio"
        
    return naturaleza

def condicion_general_r4(df_snrFMI, fmi_matriz, df_snr):
    """
        Función para comprobar si las anotaciones del folio
        cumplen con las condiciones de la regla 4
    """
    # Extrayendo las condiciones
    condiciones = condiciones_dict()
    condicionesR4P1 = condiciones["r4p1"]
    
    naturaleza = ""
    rel_tenencia = ""
    objetoOSPR = ""

    #Filtrando por anotaciones menores al 05/08/1974
    df_snrQuery = df_snrFMI.loc[(df_snrFMI["FECHA RADICACION"] >= '05/08/1974') & (df_snrFMI['ID ANOTACION'] == 1)]

    if len(df_snrQuery)>0:
        
        for condi in condicionesR4P1:
            dfquery = df_snrQuery.query(str(condi), engine='python')

            if len(dfquery)>0:
                # verifican el campo de COMPLEMENTACIONES del FMI
                condicion1 = paso2_r4_c1(df_snrFMI)

                if condicion1 == "SI":
                    naturaleza = "Privado"
                else:
                    # la sección de folio matriz
                    naturaleza = paso2_r4_c2(df_snr, fmi_matriz)
                break

    return naturaleza, rel_tenencia, objetoOSPR

def paso2_r5_c2 (df_snr, fmi_matriz):
    """
        Función para comprobar si cumplen con el paso 2 
        de la regla 5 condición 1, 2 y 3 (folios matrices)
    """
    # Extrayendo las condiciones
    condiciones = condiciones_dict()
    condicionesR5P2 = condiciones["r5p2"] #
    condicionesR5P2C1 = condiciones["r4p2c1"] #Complementaciones
    condicionesR2P1 = condiciones["r2p1"] #

    cumple = list() #Si cumple alguna de las condiciones
    matrices = fmi_matriz.split(";") #Matrices

    if len(matrices) > 0:
        for matriz in matrices:

            df_snrFMImatriz = df_snr.loc[df_snr["MATRICULA"] == matriz] #Filtrando por el matriz
            
            if len(df_snrFMImatriz) > 0:
                # Condicion 1: un código que indique la existencia de un título originario del Estado que trasfirió el dominio a un particular
                for condi in condicionesR5P2:
                    dfquery = df_snrFMImatriz.query(str(condi), engine='python')
                    if len(dfquery)>0:
                        cumple.append("SI")
                        break
            
            if not "SI" in cumple and len(df_snrFMImatriz) > 0:
                # Condicion 2: códigos que transfieren dominio  (verificando que el acto se encuentre inscritos antes del 05 de agosto de 1974)
                df_snrFMImatrizC2 = df_snrFMImatriz.loc[(df_snrFMImatriz["FECHA RADICACION"] < '05/08/1974') & (df_snrFMImatriz['ID ANOTACION'] == 1)]
                
                if len(df_snrFMImatrizC2) > 0:
                    for condi in condicionesR2P1:
                        dfquery = df_snrFMImatrizC2.query(str(condi), engine='python')
                        if len(dfquery)>0:
                            cumple.append("SI")
                            break
            
            if not "SI" in cumple and len(df_snrFMImatriz) > 0:
                # Condicion 3: Campo de COMPLEMENTACIONES del FMI matriz
                for condi in condicionesR5P2C1:
                    dfquery = df_snrFMImatriz.query(str(condi), engine='python')
                    if len(dfquery)>0:
                        cumple.append("SI")
                        break
        #Si no se cumple la CONDICION 1, 2 y 3 en el FMI matriz, 
        # se deben revisar las mismas 3 condiciones en el folio matriz de matriz 
        # y así sucesivamente.
        if not "SI" in cumple:
            matrices_matrices = list()
            fmiListM = df_snr['MATRICULA'].unique() #Lista de todos los FMI existentes en SNR
            fmiListD = df_snr['FOLIO DERIVADO'].unique() #Lista de todos los FMI derivados existentes en SNR

            for matriz in matrices:
                matriz_segre = encontrar_matriz_segregado(matriz, "NO", df_snr, fmiListM, fmiListD)
                if matriz_segre[0] != "":
                    matrices_matrices.append(matriz_segre[0]) #Asignando matrices
            print(f"--matriz matriz : {matrices_matrices}")
            matrices_matrices = ";".join(matrices_matrices)
            if len(matrices_matrices) > 0:
                naturaleza = paso2_r5_c2 (df_snr, matrices_matrices)
            else:
                naturaleza = "Baldio"

        else:    
            # En caso de contar con mas de un FMI matriz, 
            # donde se lleguen a conclusiones diferentes 
            # (uno me lleva a la conclusión de naturaleza privada y el otro de naturaleza baldía) 
            # PRIMA LA NATURALEZA BALDIA
            if len(cumple) == len(matrices):
                naturaleza = "Privado"
            else:
                naturaleza = "Baldio"
    else:
        naturaleza = "Baldio"
        
    return naturaleza

def condicion_general_r5(df_snrFMI, fmi_matriz, df_snr):
    """
        Función para comprobar si las anotaciones del folio
        cumplen con las condiciones de la regla 5
    """
    # Extrayendo las condiciones
    condiciones = condiciones_dict()
    condicionesR5P1 = condiciones["r5p1"]
    
    naturaleza = ""
    rel_tenencia = ""
    objetoOSPR = ""

    #Filtrando por la primera anotación
    df_snrQuery = df_snrFMI.loc[df_snrFMI['ID ANOTACION'] == 1]

    if len(df_snrQuery)>0:
        
        for condi in condicionesR5P1:
            dfquery = df_snrQuery.query(str(condi), engine='python')

            if len(dfquery)>0:
                # verifican el campo de COMPLEMENTACIONES del FMI
                condicion1 = paso2_r4_c1(df_snrFMI)

                if condicion1 == "SI":
                    naturaleza = "Privado"
                else:
                    # la sección de folio matriz
                    naturaleza = paso2_r5_c2(df_snr, fmi_matriz)
                break

    return naturaleza, rel_tenencia, objetoOSPR

def paso2_r7tor14_c2 (df_snr, fmi_matriz):
    """
        Función para comprobar si cumplen con el paso 2 
        de la regla 7 a regla 11 condición 1, 2 y 3 (folios matrices)
    """
    # Extrayendo las condiciones
    condiciones = condiciones_dict()
    condicionesR5P2 = condiciones["r5p2"] #
    condicionesR5P2C1 = condiciones["r4p2c1"] #Complementaciones
    condicionesR2P1 = condiciones["r2p1"] #

    cumple = list() #Si cumple alguna de las condiciones
    encontro_fmi = "" # Si no encuentra un folio
    matrices = fmi_matriz.split(";") #Matrices

    if len(matrices) > 0:
        for matriz in matrices:

            df_snrFMImatriz = df_snr.loc[df_snr["MATRICULA"] == matriz] #Filtrando por el matriz

            if len(df_snrFMImatriz) == 0:
                #Si no encuentra un folio matriz en la base snr
                encontro_fmi = 'NO'
                break
            
            if len(df_snrFMImatriz) > 0:
                # Condicion 1: un código que indique la existencia de un título originario del Estado que trasfirió el dominio a un particular
                for condi in condicionesR5P2:
                    dfquery = df_snrFMImatriz.query(str(condi), engine='python')
                    if len(dfquery)>0:
                        cumple.append("SI")
                        break
            
            if not "SI" in cumple and len(df_snrFMImatriz) > 0:
                # Condicion 2: códigos que transfieren dominio  (verificando que el acto se encuentre inscritos antes del 05 de agosto de 1974)
                df_snrFMImatrizC2 = df_snrFMImatriz.loc[(df_snrFMImatriz["FECHA RADICACION"] < '05/08/1974') & (df_snrFMImatriz['ID ANOTACION'] == 1)]
                
                if len(df_snrFMImatrizC2) > 0:
                    for condi in condicionesR2P1:
                        dfquery = df_snrFMImatrizC2.query(str(condi), engine='python')
                        if len(dfquery)>0:
                            cumple.append("SI")
                            break
            
            if not "SI" in cumple and len(df_snrFMImatriz) > 0:
                # Condicion 3: Campo de COMPLEMENTACIONES del FMI matriz
                for condi in condicionesR5P2C1:
                    dfquery = df_snrFMImatriz.query(str(condi), engine='python')
                    if len(dfquery)>0:
                        cumple.append("SI")
                        break
        #Si no se cumple la CONDICION 1, 2 y 3 en el FMI matriz, 
        # se deben revisar las mismas 3 condiciones en el folio matriz de matriz 
        # y así sucesivamente.
        if not "SI" in cumple and encontro_fmi != "NO":
            matrices_matrices = list()
            fmiListM = df_snr['MATRICULA'].unique() #Lista de todos los FMI existentes en SNR
            fmiListD = df_snr['FOLIO DERIVADO'].unique() #Lista de todos los FMI derivados existentes en SNR

            for matriz in matrices:
                matriz_segre = encontrar_matriz_segregado(matriz, "NO", df_snr, fmiListM, fmiListD)
                if matriz_segre[0] != "":
                    matrices_matrices.append(matriz_segre[0]) #Asignando matrices
            matrices_matrices = ";".join(matrices_matrices)
            if len(matrices_matrices) > 0:
                naturaleza = paso2_r5_c2 (df_snr, matrices_matrices)
            else:
                naturaleza = "Baldio"

        else:    
            # En caso de contar con mas de un FMI matriz, 
            # donde se lleguen a conclusiones diferentes 
            # (uno me lleva a la conclusión de naturaleza privada y el otro de naturaleza baldía) 
            # PRIMA LA NATURALEZA BALDIA
            if len(cumple) == len(matrices):
                naturaleza = "Privado"
            elif encontro_fmi == "NO":
                #Si NO se encuentra en la base de la SNR un  folio matriz o complementaciones no es concluyente el análisis
                naturaleza = "Por determinar"
            else:
                naturaleza = "Baldio"
    else:
        naturaleza = "Por determinar"
        
    return naturaleza

def condicion_general_r7tor14(df_snrFMI, fmi_matriz, df_snr, condicionesR7toR11P1):
    """
        Función para comprobar si las anotaciones del folio
        cumplen con las condiciones de la regla 7 PREDIOS CON GRAVAMENES 
        - HIPOTECA

    """
    
    naturaleza = ""
    rel_tenencia = ""
    objetoOSPR = ""

    #Filtrando por la primera anotación
    df_snrQuery = df_snrFMI.loc[df_snrFMI['ID ANOTACION'] == 1]

    if len(df_snrQuery)>0:
        
        for condi in condicionesR7toR11P1:
            dfquery = df_snrQuery.query(str(condi), engine='python')

            if len(dfquery)>0:
                # verifican el campo de COMPLEMENTACIONES del FMI
                condicion1 = paso2_r4_c1(df_snrFMI)

                if condicion1 == "SI":
                    naturaleza = "Privado"
                else:
                    # la sección de folio matriz
                    naturaleza = paso2_r7tor14_c2(df_snr, fmi_matriz)
                break

    return naturaleza, rel_tenencia, objetoOSPR






