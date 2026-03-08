import pulp
import pandas as pd

# 1. Входные данные (те параметры, что мы обсудили)
warehouses = ["Склад 1", "Склад 2"]
supply = {"Склад 1": 130, "Склад 2": 90}

stores = ["Магнит Семейный 1", "Магнит Экстра 1", "Магнит Экстра 2", "Магнит Семейный 2"]
demand = {
    "Магнит Семейный 1": 40,
    "Магнит Экстра 1": 70,
    "Магнит Экстра 2": 60,
    "Магнит Семейный 2": 50
}

# 2. Получение матрицы расстояний (здесь имитируем данные из вашего matrix.py)
# В реальности вы можете импортировать результат или вставить значения вручную
costs = {
    "Склад 1": {"Магнит Семейный 1": 4.5, "Магнит Экстра 1": 10.2, "Магнит Экстра 2": 15.8, "Магнит Семейный 2": 16.5},
    "Склад 2": {"Магнит Семейный 1": 18.2, "Магнит Экстра 1": 12.1, "Магнит Экстра 2": 7.4, "Магнит Семейный 2": 6.8}
}

# 3. Инициализация модели
model = pulp.LpProblem("Transportation_Optimization", pulp.LpMinimize)

# 4. Создание переменных решения (x_ij)
# Это количество паллет, отправленных со склада i в магазин j
routes = [(w, s) for w in warehouses for s in stores]
x = pulp.LpVariable.dicts("Route", (warehouses, stores), lowBound=0, cat='Integer')

# 5. Целевая функция: минимизация суммарного расстояния (дистанция * паллеты)
model += pulp.lpSum([x[w][s] * costs[w][s] for (w, s) in routes])

# 6. Ограничения
# Ограничение по запасам на складах
for w in warehouses:
    model += pulp.lpSum([x[w][s] for s in stores]) == supply[w]

# Ограничение по потребностям магазинов
for s in stores:
    model += pulp.lpSum([x[w][s] for w in warehouses]) == demand[s]

# 7. Решение задачи
status = model.solve(pulp.PULP_CBC_CMD(msg=0))

# 8. Вывод результатов
print(f"Статус решения: {pulp.LpStatus[status]}")

results = []
for w in warehouses:
    for s in stores:
        if x[w][s].varValue > 0:
            results.append({"Откуда": w, "Куда": s, "Сколько (паллет)": x[w][s].varValue})

df_res = pd.DataFrame(results)
print("\nОптимальный план перевозок:")
print(df_res)

print(f"\nОбщие логистические затраты (условные км-паллеты): {pulp.value(model.objective)}")