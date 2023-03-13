import pandas as pd

def r1_r2(insumos, textEdit, output):
    """
        Función para unificar los registros 1 y 2
    """
    print(" - 2.1 Leyendo R1")
    try:
        pathR1 = "".join([insumos, "/Registro 1.xlsx"])
        
        df_r1 = pd.read_excel(pathR1, dtype=str)
        
    except:
        pathR1 = "".join([insumos, "/Registro 1.csv"])
        df_r1 = pd.read_csv(pathR1, dtype=str, engine='python')
        

    print(" - 2.2 Leyendo R2")
    try:
        pathR2 = "".join([insumos, "/Registro 2.xlsx"])
        
        df_r2 = pd.read_excel(pathR2)
    except:
        pathR2 = "".join([insumos, "/Registro 2.csv"])
        df_r2 = pd.read_csv(pathR2)
        
    # -- Atributos de la unificación -- 
    # "DEPARTAMENTO" "MUNICIPIO" "NUMERO DE PREDIO" "Cedula Castastral 20" 
    # "Cedula Castastral 30" "NOMBRE" "NUMERO DOCUMENTO" "DIRECCION" 
    # "MATRICULA INMOBILIARIA" "AREA TERRENO" "AREA CONSTRUIDA"
    
    # Creando un dataframe donde se almacenaran la unión
    #textEdit.append(" - 2.3 Unificando por Cedula Catastral (30 dig)")
    df_r1r2 = df_r2[["numero_predial", "MATRICULA INMOBILIARIA"]].merge(df_r1[["DEPARTAMENTO", "MUNICIPIO", "NUMERO DE PREDIO", "numero_predial_anterior","numero_predial", "NOMBRE", "NUMERO DOCUMENTO", "DIRECCION", "AREA TERRENO", "AREA CONSTRUIDA"]], on = "numero_predial", how = "outer")
    
    # exportando resultado a excel
    #textEdit.append(" - 2.4 exportando resultado a excel")
    xlsPath = output + "/Unificado_Registros12.xlsx"
    df_r1r2.to_excel(xlsPath)

    return df_r1r2