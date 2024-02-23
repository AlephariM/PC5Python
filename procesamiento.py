import pandas as pd
import openpyxl

df = pd.read_excel('data/reactiva.xlsx', sheet_name = 'TRANSFERENCIAS 2020')
df.head(0)

#+++++++++++++++++++++++++++++++
def limpiar_nombres_columnas(df):
    # Convertir nombres de columna a minúsculas
    df.columns = df.columns.str.lower()
    # Eliminar espacios en los nombres de columna
    df.columns = df.columns.str.replace(' ', '_')
    # Eliminar tildes en los nombres de columna
    df.columns = df.columns.str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8')
    return df

df_1 = limpiar_nombres_columnas(df)
df_1.head(1)
#+++++++++++++++++++++++++++++++
df_2 = df_1.drop(['id', 'tipo_moneda.1'], axis= 1)
df_2.head(1)
#+++++++++++++++++++++++++++++++
df_3 = df_2
df_3['dispositivo_legal'] = df_3['dispositivo_legal'].replace({'0m':''}, regex=True)
df_3.head(1)
#+++++++++++++++++++++++++++++++
%pip install requests
import requests
from datetime import date

def obtener_tipo_cambio_sunat(fecha):
    try:
        url = f"https://api.apis.net.pe/v1/tipo-cambio-sunat?fecha={fecha}"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()['compra']
    except requests.RequestException as e:
        print("Error al obtener el tipo de cambio:", e)
        return None

fecha_actual = date.today().strftime('%Y-%m-%d')
tipo_cambio_usd = obtener_tipo_cambio_sunat(fecha_actual)

df_4 = df_3
df_4['monto_inversion_dol'] = (df_4['monto_de_inversion'] / tipo_cambio_usd).round(2)
df_4['monto_transferencia2020_dol'] = (df_4['monto_de_transferencia_2020'] / tipo_cambio_usd).round(2)
df_4 = df_4.drop('monto_dolares', axis=1)
df_4.head(3)
#+++++++++++++++++++++++++++++++
df_5 = df_4
df_5['estado'] = df_5['estado'].replace('En Ejecución', 'Ejecución')
df_5['estado'] = df_5['estado'].replace('Convenio y/o Contrato Resuelto', 'Resuelto')
df_5.estado.unique()

#+++++++++++++++++++++++++++++++
def puntuar(estado):
    valor = estado
    if (valor == 'Resuelto'):
        puntuacion = 0
    elif valor == 'Actos Previos' :
        puntuacion = 1
    elif valor == 'Ejecución' :
        puntuacion = 2
    elif valor == 'Concluido':
        puntuacion = 3
    else:
        puntuacion = None
    return puntuacion
    
df_final = df_5
df_final['puntuación'] = df_final['estado'].apply(puntuar)
df_final.head(2)

#+++++++++++++++++++++++++++++++
import sqlite3

# Conectar a la base de datos (se creará si no existe)
conexion = sqlite3.connect('ubicaciones.db')

# Extraer datos únicos de las columnas 'ubigeo', 'Region', 'Provincia' y 'Distrito'
datos_ubigeo = df_final[['ubigeo', 'region', 'provincia', 'distrito']].drop_duplicates()

# Crear una tabla en la base de datos SQLite y almacenar los datos
datos_ubigeo.to_sql('ubigeo', conexion, if_exists='replace', index=False)

# Confirmar y cerrar la conexión
conexion.commit()
conexion.close()

print("Tabla de ubigeos almacenada en la base de datos.")


#+++++++++++++++++++++++++++++++
# Tipo de obra 'Urbano' y estado 1, 2 o 3
condicion1 = (df_final['tipologia'] == 'Equipamiento Urbano') & (df_final['puntuación'] >= 1) & (df_final['puntuación'] <= 3)
df_filtrado = df_final[condicion1]

# Lista de regiones unicas
Lista_reg_unicas = df_filtrado['region'].unique()

for region in Lista_reg_unicas:
    # Filtrar los datos por región
    condicion2 = df_filtrado['region'] == region
    df_region = df_filtrado[condicion2]
    # Verificar si hay datos para la región actual
    if not df_region.empty:
        
        df_region_ordenado = df_region.sort_values(by='monto_de_inversion', ascending=False)
        
        top_5_obras = df_region_ordenado.head(5)
        
        # Guardar el resultado en un archivo Excel
        nombre_archivo = f"t5_inversion_{region}.xlsx"
        top_5_obras.to_excel(nombre_archivo, index=False)
        print(f"Archivo '{nombre_archivo}' generado correctamente.")
    else:
        print(f"No hay datos para la región '{region}'. No se generará el reporte.")