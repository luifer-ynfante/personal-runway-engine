import pandas as pd
import os

def procesar_extracto():
    print("Iniciando motor de categorización...")
    
    # Rutas de entrada y salida
    ruta_script = os.path.dirname(__file__)
    ruta_input = os.path.join(ruta_script, '..', 'data', 'banco_raw.csv')
    ruta_output = os.path.join(ruta_script, '..', 'data', 'flujo_caja_limpio.csv')
    
    # 1. Leer el archivo sucio del banco
    df = pd.read_csv(ruta_input)
    
    # 2. Diccionario de reglas (El "cerebro" del categorizador)
    def asignar_categoria(concepto):
        concepto = concepto.upper()
        if 'SEPE' in concepto:
            return pd.Series(['Ingresos', 'Prestacion SEPE', 'Ingreso'])
        elif 'IBERDROLA' in concepto:
            return pd.Series(['Suministros', 'Luz y Gas', 'Gasto Fijo'])
        elif 'MERCADONA' in concepto:
            return pd.Series(['Supervivencia', 'Supermercado', 'Gasto Variable'])
        else:
            return pd.Series(['Otros', concepto, 'Gasto Variable'])

    # Aplicar las reglas a cada fila
    df[['categoria', 'concepto', 'tipo_movimiento']] = df['Concepto'].apply(asignar_categoria)
    
    # 3. Limpieza de formato para Power BI
    df['monto'] = df['Importe'].abs() # Quita el signo negativo de los gastos
    df['dia_mes'] = pd.to_datetime(df['Fecha'], format='%d/%m/%Y').dt.day
    
    # 4. Ordenar y exportar
    df_final = df[['categoria', 'concepto', 'tipo_movimiento', 'monto', 'dia_mes']]
    df_final.to_csv(ruta_output, index=False)
    
    print(f"¡Éxito! Archivo procesado y guardado en: data/flujo_caja_limpio.csv")

if __name__ == "__main__":
    procesar_extracto()