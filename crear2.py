import pandas as pd
import random

# Cantidad de cada vehículo (Se adapta a cualquier tamaño de empresa)
Furgoneta = 5
Auto = 5
Moto = 7
Bici = 5
num_vehiculos = Furgoneta+Auto+Moto+Bici

# Rango de pedidos, basado en la cantidad máxima q se puede recibir si todos los pedidos quedadn a 15 kilómetros
Rango_pedidos = (Furgoneta*11)+(Auto*11)+(Moto*12)+(Bici*9)-48

# Define los parámetros de generación de datos para pedidos
# num_pedidos = random.randint(int(Rango_pedidos/2), Rango_pedidos)  # Número de pedidos aleatorio entre su capacidad máxima y media capacidad
num_pedidos = int(Rango_pedidos) #Numero de pedidos fijo para poder trabajar con los mismos pedidos en el analisis de sensibilidad
max_distancia = 15000  # Distancia máxima en kilómetros
max_volumen = 3.3  # Volumen máximo en metros cúbicos
max_minuto_laboral = 780  # Minuto laboral máximo

# Límites para volumenes
volumen_min = 0.01

# Proporciones según vehículos:
Resto = (num_pedidos%num_vehiculos)
P_F = (num_pedidos//num_vehiculos)*Furgoneta
P_A = (num_pedidos//num_vehiculos)*Auto
P_M = (num_pedidos//num_vehiculos)*Moto
P_B = ((num_pedidos//num_vehiculos)*Bici)+Resto

# Genera datos aleatorios para pedidos
data_pedidos = {
    'Pedido': list(range(1, num_pedidos + 1)),
    'Distancia': [random.uniform(500, max_distancia) for _ in range(num_pedidos)],
    'Volumen': (
        [random.uniform(volumen_min, 3.3) for _ in range(P_F)] +
        [random.uniform(volumen_min, 0.3) for _ in range(P_A)] +
        [random.uniform(volumen_min, 0.07) for _ in range(P_M)] +
        [random.uniform(volumen_min, 0.07) for _ in range(P_B)]
    ),
    'MinutoLaboral': [random.randint(0, max_minuto_laboral) for _ in range(num_pedidos)]
}

# Crea un DataFrame para pedidos
df_pedidos1 = pd.DataFrame(data_pedidos)

# Define los datos de tipos de vehículos
data_vehiculos = {
    'Tipo': [1, 2, 3, 4],
    'CapacidadVolumen': [3.3, 0.3, 0.07, 0.07],
    'CantidadCO2': [0.000121, 0.000094, 0.000167, 0],
    'CostoOperacion': [0.14534051844, 0.0988392, 0.041118, 0],
    'VelocidadPromedio': [6.94, 6.94, 7.634, 5.91667],
    'Cantidad': [Furgoneta, Auto, Moto, Bici]  # Cantidad aleatoria random.randint(1, num_vehiculos) for _ in range(4)
}

# Crea un DataFrame para tipos de vehículos
df_vehiculos1 = pd.DataFrame(data_vehiculos)

#cosas
print('numero de pedidos:', str(num_pedidos))
print('numero de vehiculos:', str(num_vehiculos))
print('Proporciones:')
print('Furgoneta:', str(P_F))
print('Auto:', str(P_A))
print('Motos:', str(P_M))
print('Bicicleta:', str(P_B))

# Muestra los primeros registros de los DataFrames para verificar
print("DataFrame de Pedidos:")
print(df_pedidos1.head())

print("\nDataFrame de Tipos de Vehículos:")
print(df_vehiculos1.head())

df_pedidos1.to_csv('data_pedidos.csv', index=False)
df_vehiculos1.to_csv('data_vehiculos.csv', index=False)