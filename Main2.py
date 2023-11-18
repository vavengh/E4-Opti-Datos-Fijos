from gurobipy import GRB, Model, quicksum 
import pandas as pd
from matplotlib import pyplot as plt
# Importa num_pedidos desde otro archivo
# from crear2 import num_pedidos


# Cantidad de cada vehículo (Se adapta a cualquier tamaño de empresa)
Furgoneta = 5
Auto = 5
Moto = 7
Bici = 5

# Define los parámetros de generación de datos para pedidos
# num_pedidos = random.randint(int(Rango_pedidos/2), Rango_pedidos)  # Número de pedidos aleatorio entre su capacidad máxima y media capacidad



df_pedidos = pd.read_csv('data_pedidos.csv')
df_vehiculos = pd.read_csv('data_vehiculos.csv')

# Conjuntos:
T = range(0,480) #tiempo del dia
K = range(1,4) #1 Auto grande, 2 Auto chico, 3 Moto, 4 Bici
I = range(1, 150)  # Cambiar el límite superior a num_pedidos
#indices de los pedidos
print('T:', T)
print('K:',K)
print('I:', I)
# Reemplazar los DataFrames df_pedidos y df_vehiculos con los nombres de parámetros
V_k = df_vehiculos['CapacidadVolumen'].tolist()
D_i = df_pedidos['Distancia'].tolist()
C_k = df_vehiculos['CantidadCO2'].tolist()
O_k = df_vehiculos['CostoOperacion'].tolist()
H_i = df_pedidos['Volumen'].tolist()
VEL_k = df_vehiculos['VelocidadPromedio'].tolist()
N_k = df_vehiculos['Cantidad'].tolist()
P = 400000000  # Este valor puede ser asignado directamente
B_i = df_pedidos['MinutoLaboral'].tolist()

m = Model()
m.setParam('TimeLimit', 45*60)

# Variables de decision

#Si tomo el pedido i al vehiculo k en el bloque t
# Variables de decisión
X = m.addVars(I, K, T, vtype=GRB.BINARY, name="X")
Y = m.addVars(K, T, vtype=GRB.BINARY, name="Y")
S = m.addVars(K, T, vtype=GRB.BINARY, name="S")

# Restricciones

# Restricción 1: No se pueden utilizar más vehículos de los que tiene disponible la empresa al mismo tiempo
m.addConstrs((Y[k, t] <= N_k[k] - quicksum(X[i, k, t] for i in I) for k in K for t in T), name="R1")

# Restricción 2: Se debe asignar solo un tipo de vehículo para cada pedido
m.addConstrs((quicksum(X[i, k, t] for k in K) <= 1 for t in T for i in I), name="R2")


# Restricción 3: Volumen del pedido no puede superar la capacidad del vehículo
m.addConstrs((quicksum(X[i, k, t] * H_i[i] for i in I) <= V_k[k] for k in K for t in T), name="R3")


# Restricción 4: No se puede superar el presupuesto diario
m.addConstr((quicksum(X[i, k, t] * O_k[k] * D_i[i] for i in I for k in K for t in T) <= P), name="R4")


# Restricción 5: Un repartidor no puede repartir un producto al cual no alcance a volver a tiempo
m.addConstrs((X[i, k, t] * (1 / 60) * (D_i[i] / VEL_k[k]) <= 480 - B_i[i] for k in K for t in T for i in I), name="R5")


# Restricción 6: Para poder asignar el tipo de vehículo k al pedido i en el tiempo t, este vehículo debe estar disponible
m.addConstrs((X[i, k, t] <= Y[k, t] for k in K for t in T for i in I), name="R6")

# Restricción 7: Cada pedido i debe ser entregado en un rango de 2 horas a partir de la hora solicitada (b_i)
m.addConstrs((quicksum(X[i, k, t] for t in range(0, max(0, B_i[i] - 60))) <= (D_i[i] / (60 * VEL_k[k])) for k in K for i in I), name="R7a")
m.addConstrs((quicksum(X[i, k, t] for t in range(B_i[i] + 60, 480)) <= (D_i[i] / (60 * VEL_k[k])) for k in K for i in I), name="R7b")
#m.addConstrs((quicksum(X[i, k, t] for t in range(0, 840)) == ((D_i[i] * 2) / (VEL_k[k]*60)) for k in K for i in I), name="R7c")
m.addConstr((quicksum(X[i, k, t] for t in T for i in I for k in K) >= quicksum(1 for i in I)), name="R7c")

# Restricción 8: El conductor de cada vehículo k debe descansar mínimo 45 minutos diarios
m.addConstrs((quicksum(S[k, t] for t in T) >= 45 for k in K), name="R8")

# Restricción 9: Solo un tipo de vehículo {k} puede estar descansando a la vez
m.addConstrs((quicksum(S[k, t] for k in K) <= 1 for t in T), name="R9")

# R10: Si el conductor del vehículo k está en descanso, no es posible asignarle un pedido
m.addConstrs((S[k, t] + Y[k, t] <= 1 for t in T for k in K), name="R10")






#FO
m.update()

obj = quicksum(X[i, k, t] * C_k[k] * 2 * D_i[i] for i in I for k in K for t in T)
m.setObjective(obj, GRB.MINIMIZE)

m.optimize()

tiempo_transcurrido = m.Runtime
if tiempo_transcurrido >= 45*60:  # Si el tiempo transcurrido es mayor o igual a 60 segundos
    m.terminate()

m.printAttr("ObjVal")
#print("Número de variables: ", m.NumVars)
#print("Número de restricciones: ", m.NumConstrs)

valor_objetivo = m.ObjVal
print(f"Valor objetivo: {valor_objetivo}")

print('\n ----------------------------------------------------------- \n')

# Crear una lista para almacenar los resultados
resultados = []

# Recorrer las variables X
for i in I:
    for k in K:
        w = 0
        for t in T:
            # Verificar si la variable de decisión X es igual a 1
            if X[i, k, t].x == 1:
                w = 1
        if w == 1:
            resultados.append({
                'Pedido': i,
                'Vehiculo': k,
                'Tiempo entrega': B_i[i]
            })
            w = 0


# Crear un DataFrame de pandas a partir de la lista de resultados
df_resultados = pd.DataFrame(resultados)

# Guardar la tabla de resultados en un archivo Excel
df_resultados.to_excel('resultados.xlsx', index=False)

# Mostrar la tabla de valores de las variables de decisión
print(df_resultados)

