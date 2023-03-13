from api_ant.core.fun_generales import *
import pandas as pd


def fmiCat_enSNR(cedCat_fmi_list, gdf_CatUnificado, snr_fmi_list, df_snr, feedback):
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
        list_DocsID_Cat = gdf_CatUnificadoFilter["NUMERO DOCUMENTO"].astype(str) # Lista Documentos de identidad Catastro Unificado
        list_noms_Catastro = gdf_CatUnificadoFilter["NOMBRE"].astype(str) #Lista Nombres Catastro Unificado
        list_noms_Catastro.replace("nan", "") #Quitando valores con nan

        #feedback.pushInfo(" - - - tamaño filtro cat {}".format(len(gdf_CatUnificadoFilter)))
        #feedback.pushInfo(" - - - cols {}".format(gdf_CatUnificadoFilter.columns))
        departamento = str(gdf_CatUnificadoFilter["DEPARTAMENTO"].values[0])
        municipio = str(gdf_CatUnificadoFilter["MUNICIPIO"].values[0])
        id_predial = str(gdf_CatUnificadoFilter["id_predial"].values[0]).zfill(10)
        ced_cat = str(gdf_CatUnificadoFilter["numero_predial"].values[0])
        ced_cat_ant = str(gdf_CatUnificadoFilter["numero_predial_anterior"].values[0])
        direccion = str(gdf_CatUnificadoFilter["DIRECCION"].values[0])
        clasifica_suelo_pot = str(gdf_CatUnificadoFilter["clasifica_suelo_pot"].values[0])
        area_terreno_igac = str(gdf_CatUnificadoFilter["AREA TERRENO"].values[0])
        area_construida = str(gdf_CatUnificadoFilter["AREA CONSTRUIDA"].values[0])
        fmiCat = str(gdf_CatUnificadoFilter["MATRICULA INMOBILIARIA"].values[0])
        area_geografica = gdf_CatUnificadoFilter["area_terreno_geografica"].values[0]
        #feedback.pushInfo(" ".join([fmiCat, ced_cat, datoCatastro]))

        if ced_cat != "nan" and ced_cat != "" and ced_cat != None:
            
            # Filtrando en SNR por FMI de catastro y por propietario
            df_snr_filterFMI = df_snr[df_snr["MATRICULA"] == fmiCat]
            tipo_predio_snr = df_snr_filterFMI["TIPO PREDIO"].str.upper()
            df_snr_filter = df_snr_filterFMI[df_snr_filterFMI['PROPIETARIO'] == "X"]
            # orden descendente en ID ANOTACION
            df_snr_filter["ID ANOTACION"] = df_snr_filter["ID ANOTACION"].astype(int)
            df_snr_filter = df_snr_filter.sort_values(by='ID ANOTACION', ascending=False) 
            list_IDanotacion = df_snr_filter["ID ANOTACION"] #Lista de ID anotacion 
            list_DocsID_SNR = df_snr_filter["NRO DOCUMENTO"] #Lista Documentos de identidad SNR
            list_noms_SNR = df_snr_filter["NOMBRES"] #Lista Nombres SNR
            
            if(fmiCat == "" or fmiCat == "nan" or fmiCat == None):

                interrelacionCatSNR = "1" #Interrelacion Catastro registro: Sin folio
                ultimo_propietario_snr = ""
                cedCat_fmi = ""
                fmiActivo = ""
                fmiDireccion = ""
                # Coincidencia Catastro Registro
                coincidePropietario = "3" #Sin interrelación
                propietarioCatastro = list_noms_Catastro.values[0] #Se toma cualquier nombre de la lista de catastro Unificado
                
                urbano = "SI"
                
            elif ((snr_fmi_list == fmiCat).any()):

                interrelacionCatSNR = "2" #Interrelacion Catastro registro: interrelacion
                cedCat_fmi = str(df_snr_filterFMI['NROCATASTRO'].values[0])
                fmiEstado = str(df_snr_filterFMI['ESTADO_FOLIO'].values[0])
                fmiDireccion = str(df_snr_filterFMI['DIRECCION'].values[0])
                fmiActivo = fmi_activo(str(fmiEstado))
                if (len(list_IDanotacion)>0):
                    ultima_IDanotacion = list_IDanotacion.values[0]
                    df_snr_ultimoProp = df_snr_filter[df_snr_filter["ID ANOTACION"] == ultima_IDanotacion]
                    nombres_ultimoProp = df_snr_ultimoProp["NOMBRES"]
                    otro = y_otro(nombres_ultimoProp)
                    ultimo_propietario_snr = "".join([str(nombres_ultimoProp.values[0]), otro])
                else:
                    ultimo_propietario_snr = ""
                propietarioCatastro, coincidePropietario, df_comparacion = compararPropietarioCatSnr(list_DocsID_Cat, list_DocsID_SNR, list_noms_Catastro, list_noms_SNR, list_IDanotacion, df_comparacion)
                
                tipo_predio_snr = tipo_predio_snr.values[0]

                if (tipo_predio_snr == "URBANO" and clasifica_suelo_pot == "1"):
                    urbano = "SI"
                else:
                    urbano = "NO"
            else:

                interrelacionCatSNR = "3" #Interrelacion Catastro registro: Solo en Catastro
                ultimo_propietario_snr = ""
                cedCat_fmi = ""
                fmiActivo = ""
                fmiDireccion = ""
                # Coincidencia Catastro Registro
                coincidePropietario = "3" #Sin interrelación
                propietarioCatastro = str(list_noms_Catastro.values[0]) #Se toma cualquier nombre de la lista de catastro Unificado
                
                urbano = "SI"

            
            # Cuando hay más un propietario registrado en Catastro
            otro = y_otro(list_noms_Catastro)
            propietarioCatastro = "".join([propietarioCatastro, otro])

            #Aplicando función para categorizar el folio en sistema actual y antiguo
            circulo, folio, antiguo = separar_folio(fmiCat)

            row = {
                    "fmi":fmiCat, "id_predial": id_predial, "departamento": departamento,  
                    "municipio": municipio, "numero_predial": ced_cat,  
                    "numero_predial_anterior": ced_cat_ant, "circulo_registral": circulo, 
                    "numero_matricula": folio, "antiguo_sistema_registro": antiguo, 
                    "interrelacion_cat_reg": interrelacionCatSNR, "propietario_catastro": propietarioCatastro, 
                    "coincidencia_propietario": coincidePropietario,"area_terreno_r1": area_terreno_igac, 
                    "area_construida_r1":area_construida, 'area_terreno_geografica':area_geografica,
                    "clasificacion_suelo_pot": clasifica_suelo_pot, "ultimo_propietario_fmi": ultimo_propietario_snr, 
                    "nombre_predio_catastro": direccion, "nombre_predio_snr": fmiDireccion,"fmi_activo": fmiActivo, "cedula_catastral_fmi": cedCat_fmi, "urbano":urbano
                }
            df_api = df_api.append(row, ignore_index = True)
        else:
            pass
    
    return df_api, df_comparacion
    
def Adicion_fmiSNR(df_api, snr_fmi_list, df_snr):
    """
        Función para adicionar folios de la SNR que no estan
        en Catastro Unificado
    """
    fmi_api_list = df_api["fmi"] #Folios existentes en df api
    
    for fmi_snr in snr_fmi_list:
        if (fmi_api_list == fmi_snr).any():
            pass
        else:
            # Filtrando en SNR por FMI
            df_snr_filterFMI = df_snr[df_snr["MATRICULA"] == fmi_snr]
            df_snr_filter = df_snr_filterFMI[df_snr_filterFMI['PROPIETARIO'] == "X"]
            df_snr_filter["ID ANOTACION"] = df_snr_filter["ID ANOTACION"].astype(int)
            df_snr_filter = df_snr_filter.sort_values(by='ID ANOTACION', ascending=False)
            list_IDanotacion = df_snr_filter["ID ANOTACION"] #Lista de ID anotacion 
            interrelacionCatSNR = "0" #Interrelacion Catastro registro: Solo en SNR
            if (len(list_IDanotacion)>0):
                ultima_IDanotacion = list_IDanotacion.values[0]
                df_snr_ultimoProp = df_snr_filter[df_snr_filter["ID ANOTACION"] == ultima_IDanotacion]
                nombres_ultimoProp = df_snr_ultimoProp["NOMBRES"]
                otro = y_otro(nombres_ultimoProp)
                ultimo_propietario_snr = "".join([str(nombres_ultimoProp.values[0]), otro])
            else:
                ultimo_propietario_snr = ""
            cedCat_fmi = str(df_snr_filterFMI['NROCATASTRO'].values[0])
            fmiEstado = str(df_snr_filterFMI['ESTADO_FOLIO'].values[0])
            fmiDireccion = str(df_snr_filterFMI['DIRECCION'].values[0])
            fmiActivo = fmi_activo(str(fmiEstado))
            # Coincidencia Catastro Registro
            coincidePropietario = "3" #Sin interrelación

            #Aplicando función para categorizar el folio en sistema actual y antiguo
            circulo, folio, antiguo = separar_folio(fmi_snr) 

            row = {
                "fmi":fmi_snr, "circulo_registral": circulo, "numero_matricula": folio, 
                "antiguo_sistema_registro": antiguo, "interrelacion_cat_reg": interrelacionCatSNR, 
                "ultimo_propietario_fmi": ultimo_propietario_snr, "coincidencia_propietario": coincidePropietario, 
                "fmi_activo": fmiActivo, "cedula_catastral_fmi": cedCat_fmi, "urbano":"NO", "nombre_predio_snr": fmiDireccion,
            }
            df_api = df_api.append(row, ignore_index = True)
    
    return df_api
    
def compararPropietarioCatSnr(list_DocsID_Cat, list_DocsID_SNR, list_noms_Catastro, list_noms_SNR, list_IDanotacion, df_comparacion):
    """
        Función para comparar la coincidencia del propietario en 
        catastro y en registro 
    """
    if (len(list_DocsID_SNR) > 0):
        # Comparación por documentos de identidad
        i = 0 # Contador para saber si coincide con propietario actual o anterior 
        for docIDsnr in list_DocsID_SNR:
            if (list_DocsID_Cat == docIDsnr).any():
                indice = list_DocsID_Cat.where(list_DocsID_Cat == docIDsnr).index.values[0] # indice en lista de documentos para obtener el nombre de Catastro
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
                nombre_snr_normal = normalizar(nombre_snr)
                for nombre_cat in list_noms_Catastro:
                    nombre_cat_normal = normalizar(nombre_cat)
                    comparacion, porcentaje = compara_nombres(nombre_snr_normal, nombre_cat_normal)
                    df_comparacion = df_comparacion.append({"Nombre SNR":nombre_snr_normal, "Nombre Catastro":nombre_cat_normal, "Porcentaje":porcentaje}, ignore_index = True)
                    if comparacion == "IGUAL": #Si coindicen que pare el bucle 
                        break
                if comparacion == "IGUAL": #Si coindicen que pare el bucle
                    break
                i += 1
        propietarioCatastro = nombre_cat
        
    else:

        propietarioCatastro = str(list_noms_Catastro.values[0])
        comparacion = ""
        
    # Determinando la coincidencia y nombre de propietario catastro
    if (comparacion == "IGUAL" and i == 0):
        coincidePropietario = "0" #Coincide con actual propietario
    elif(comparacion == "IGUAL" and i > 0):
        
        if (list_IDanotacion.values[0] == list_IDanotacion.values[i]): #Si hay más de un propietario con el mismo ID anotación
            coincidePropietario = "0" #Coincide con actual propietario
        else:
            coincidePropietario = "2" #Coincide con un propietario anterior

    else:
        coincidePropietario = "1" #No Coinciden
    
    return propietarioCatastro, coincidePropietario, df_comparacion

    
def catastro_SNR(feedback, insumos, gdf_CatUnificado, output):
    """
        Función para cruzar catastro unificado y snr
    """
    #Leyendo Base Registral SNR
    print(" - 4.1 Leyendo Base Registral SNR")
    try:
        
        pathSNR = "".join([insumos, "/Base Registral Snr.xlsx"])
        df_snr = pd.read_excel(pathSNR, dtype=str) #df de SNR

    except:
        pathSNR = "".join([insumos, "/Base Registral Snr.csv"])
        df_snr = pd.read_csv(pathSNR, dtype=str, engine='python', error_bad_lines=False) #df de SNR
    
    
    #Quitando espacios y ceros a la izquierda
    print(" - 4.2 Normalizando campos")   
    
    #Normalizando 
    df_snr["MATRICULA"] = df_snr.apply(lambda x: quitar_ceros(x["MATRICULA"]), axis=1)
    df_snr["MATRICULA"] = df_snr.apply(lambda x: normalizar_fmi(x["MATRICULA"]), axis=1)
    df_snr["FOLIO DERIVADO"] = df_snr.apply(lambda x: quitar_ceros(x["FOLIO DERIVADO"]), axis=1)
    df_snr["FOLIO DERIVADO"] = df_snr.apply(lambda x: normalizar_fmi(x["FOLIO DERIVADO"]), axis=1)
    df_snr["NRO DOCUMENTO"] = df_snr.apply(lambda x: quitar_ceros(x["NRO DOCUMENTO"]), axis=1)
    snr_fmi_list = df_snr["MATRICULA"].unique() #Series de FMI en SNR

    print(" - 4.3 Obteniendo los valores unicos (CedulaCatastral-fmi) de Catastro unificado")
    gdf_CatUnificado["cedCat_fmi"] = gdf_CatUnificado["numero_predial"].astype(str) + "_" + gdf_CatUnificado["MATRICULA INMOBILIARIA"].astype(str) 
    cedCat_fmi_list = gdf_CatUnificado["cedCat_fmi"].unique() #Lista de FMI en Catastro Unificado

    print(" - 4.4 Verificando interrelación catastro Registro")
    print("    - - 4.4.1 Folios de Catastro presentes en SNR (cedula_cat_fmi) - Coincidencia propietario")
    df_api1, df_comparacion = fmiCat_enSNR(cedCat_fmi_list, gdf_CatUnificado, snr_fmi_list, df_snr, feedback)

    print("    - - 4.4.2 Adicionando folios de SNR que no se relacionan con Catastro (tipo rural y sin info)")
    #Filtrando por tipo de predio RURAL Y SIN INFORMACIÓN
    df_snr_rural = df_snr[df_snr["TIPO PREDIO"].str.upper() != "URBANO"]
    snr_fmi_list_rural = df_snr_rural["MATRICULA"].unique()#Lista de FMI en SNR
    df_api2 = Adicion_fmiSNR(df_api1, snr_fmi_list_rural, df_snr_rural)

    #Definiendo el nombre de departamento y municipio para todos los datos
    df_api2["departamento"] = df_api1["departamento"].unique()[0]
    df_api2["municipio"] = df_api1["municipio"].unique()[0]
    
    print(" - 4.5 Folios Matrices y Segregados")
    fmiListM = df_snr['MATRICULA'].unique() #Lista de todos los FMI existentes en SNR
    fmiListD = df_snr['FOLIO DERIVADO'].unique()
    df_api2[['fmi_matriz', 'fmi_segregado']] = df_api2.apply(lambda x: encontrar_matriz_segregado(x["fmi"], x["urbano"], df_snr, fmiListM, fmiListD), axis=1)
    #del df_api2["fmi"] #Eliminando fmi
    #del df_api2["urbano"] #Eliminando urbano
    df_api2 = df_api2.fillna("")
    df_api_preliminar = df_api2.replace(to_replace="nan",value="")

    # exportando resultado a excel
    print(" - - 4.6 exportando resultado a excel")
    xlsPath = output + "/api_preliminar.xlsx"
    df_api_preliminar.to_excel(xlsPath)

    # Exportando comparación de nombres a excel
    xlsPath = output + "/Comparacion_Nombres.xlsx"
    df_comparacion.to_excel(xlsPath)

    return df_api_preliminar