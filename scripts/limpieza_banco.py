import pandas as pd
import os
import glob

def procesar_extracto():
    print("Iniciando motor de categorización avanzado...")
    
    ruta_script = os.path.dirname(__file__)
    ruta_datos = os.path.join(ruta_script, '..', 'data')
    
    # 1. Buscar automáticamente el archivo del banco
    archivos_banco = glob.glob(os.path.join(ruta_datos, '*.xls*'))
    
    if not archivos_banco:
        print("Error: No se encontró ningún archivo Excel en la carpeta data.")
        return
        
    ruta_input = archivos_banco[0]
    print(f"Archivo detectado: {os.path.basename(ruta_input)}")
    
    # 2. Leer el Excel de forma inteligente
    df_raw = pd.read_excel(ruta_input, header=None)
    header_idx = 0
    for i, row in df_raw.iterrows():
        if 'Concepto' in list(row.values) or 'Importe' in list(row.values):
            header_idx = i
            break
            
    df = pd.read_excel(ruta_input, header=header_idx)
    
    # 3. Diccionario de reglas (El "cerebro" del categorizador)
    def asignar_categoria(fila):
        concepto = str(fila['Concepto']).upper()
        importe = fila['Importe']
        
        # INGRESOS
        if 'SEPE' in concepto:
            return pd.Series(['Ingresos', 'Prestacion SEPE', 'Ingreso Fijo'])
        elif 'NOMINA' in concepto or 'CLIPISO' in concepto:
            return pd.Series(['Ingresos', 'Nómina', 'Ingreso Fijo'])
        elif 'ABONO BIZUM' in concepto: 
            return pd.Series(['Ingresos', 'Bizum Recibido', 'Ingreso Variable'])
            
        # VIVIENDA Y LEGAL
        elif 'CARLOS PRIETO' in concepto:
            return pd.Series(['Vivienda', 'Alquiler', 'Gasto Fijo'])
        elif 'ARTURO RODRIGUEZ' in concepto:
            return pd.Series(['Legal', 'Abogado Despido', 'Gasto Excepcional'])
            
        # GASTOS FIJOS Y SUPERVIVENCIA
        elif 'IBERDROLA' in concepto or 'REPSOL' in concepto:
            return pd.Series(['Suministros', 'Luz y Gas', 'Gasto Fijo'])
        elif any(x in concepto for x in ['MERCADONA', 'CARREFOUR', 'ALDI', 'DIA', 'ALIMENTACION']):
            return pd.Series(['Supervivencia', 'Supermercado', 'Gasto Necesario'])
        elif 'METRO' in concepto or 'RENFE' in concepto:
            return pd.Series(['Supervivencia', 'Transporte', 'Gasto Necesario'])
        elif 'SANITAS' in concepto:
            return pd.Series(['Salud', 'Seguro Médico', 'Gasto Fijo'])
        elif 'VODAFONE' in concepto:
            return pd.Series(['Telecomunicaciones', 'Internet/Móvil', 'Gasto Fijo'])
        
        # EL CASO LINKEDIN (Separando el error)
        elif 'LINKEDIN' in concepto:
            if importe < -100:
                return pd.Series(['Gastos Excepcionales', 'Error LinkedIn (Reclamado)', 'Gasto Evitable'])
            else:
                return pd.Series(['Formación', 'Software y Upskilling', 'Gasto Fijo'])
        elif 'MICROSOFT' in concepto:
            return pd.Series(['Formación', 'Software y Upskilling', 'Gasto Fijo'])
            
        # DEUDAS Y PRÉSTAMOS
        elif any(x in concepto for x in ['COFIDIS', 'PEPPER', 'CAIXABANK PAYMENTS', 'BILBAO VIZCAYA', 'FLOA']):
            return pd.Series(['Deudas', 'Cuota Préstamo', 'Gasto Fijo'])

        # EL DETECTOR DE FUGAS Y OCIO
        elif 'BIZUM' in concepto: 
            return pd.Series(['Ocio (Fuga)', 'Bizum a amigos', 'Gasto Evitable'])
        elif any(x in concepto for x in ['UBER', 'GLOVO', 'JUSTEAT', 'JUST EAT', 'BURGER', 'MCDONALDS', 'KFC', 'PAPA JOHNS', 'SUSHI']):
            return pd.Series(['Ocio (Fuga)', 'Comida a Domicilio/Fast Food', 'Gasto Evitable'])
        elif any(x in concepto for x in ['BAR', 'CERVECERIA', 'YATE', 'CONSUMICIONES', 'EVENTOS', 'VIVATICKET']):
            return pd.Series(['Ocio (Fuga)', 'Bares y Salidas', 'Gasto Evitable'])
        elif any(x in concepto for x in ['BAKERY', 'CAFE', 'DULCE TACHIRA', 'MINA SPECIALTY']):
            return pd.Series(['Ocio (Fuga)', 'Cafetería/Antojos', 'Gasto Evitable'])
        elif any(x in concepto for x in ['FORTNITE', 'PRIME', 'GOOGLE PLAY']):
            return pd.Series(['Ocio (Fuga)', 'Juegos y Suscripciones', 'Gasto Evitable'])
            
        # LO QUE AÚN NO RECONOCE
        else:
            tipo = 'Ingreso Raro' if importe > 0 else 'Gasto No Identificado'
            return pd.Series(['Otros', concepto, tipo])

    # Aplicar las reglas
    df[['categoria', 'concepto_limpio', 'tipo_movimiento']] = df.apply(asignar_categoria, axis=1)
    
    # 4. Limpieza de formato para Power BI
    df.rename(columns={'F. Operativa': 'Fecha', 'concepto_limpio': 'concepto'}, inplace=True)
    df['monto'] = df['Importe'].abs()
    df['dia_mes'] = pd.to_datetime(df['Fecha'], format='%d/%m/%Y').dt.day
    
    # 5. Ordenar y exportar
    ruta_output = os.path.join(ruta_datos, 'flujo_caja_limpio.csv')
    df_final = df[['categoria', 'concepto', 'tipo_movimiento', 'monto', 'dia_mes']]
    df_final.to_csv(ruta_output, index=False, encoding='utf-8-sig')
    
    print(f"¡Éxito! El archivo ha sido devorado y transformado.")

if __name__ == "__main__":
    procesar_extracto()
    