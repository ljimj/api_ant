import pandas as pd

def r1_r2(insumos, feedback, output):
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