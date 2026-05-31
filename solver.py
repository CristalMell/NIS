import pulp

# 1. Входные данные (оцифровка с картинки)
suppliers = ["П1", "П2"]
dcs = ["РЦ1", "РЦ2", "РЦ3"]
stores = ["М1", "М2", "М3", "М4"]

# Вычисленная потребность каждого магазина
demand = {"М1": 15, "М2": 15, "М3": 15, "М4": 15}

# Затраты на логистику (за 1 единицу)
cost_p_rc = {
    "П1": {"РЦ1": 10, "РЦ2": 50, "РЦ3": 30},
    "П2": {"РЦ1": 50, "РЦ2": 40, "РЦ3": 15}
}
cost_rc_m = {
    "РЦ1": {"М1": 2, "М2": 2, "М3": 50, "М4": 50},
    "РЦ2": {"М1": 50, "М2": 50, "М3": 1, "М4": 1},
    "РЦ3": {"М1": 35, "М2": 20, "М3": 10, "М4": 5}
}

# Характеристики машины (выбираем Тип 1, так как он очевидно выгоднее для прямых рейсов)
vehicle_cap = 15
vehicle_fixed_cost = 1500

# 2. Инициализация модели
model = pulp.LpProblem("MultiEchelon_Optimization", pulp.LpMinimize)

# 3. Переменные
# x[p][dc][m] - объем товара, идущего транзитом от П через РЦ в М
x = pulp.LpVariable.dicts("Flow", 
                          ((p, dc, m) for p in suppliers for dc in dcs for m in stores), 
                          lowBound=0, cat='Integer')

# v[dc][m] - количество нанятых машин от РЦ до Магазина
v = pulp.LpVariable.dicts("Vehicles",
                          ((dc, m) for dc in dcs for m in stores),
                          lowBound=0, cat='Integer')

# 4. Целевая функция: Переменные (на единицу) + Фиксированные (на машину)
var_costs = pulp.lpSum([x[p, dc, m] * (cost_p_rc[p][dc] + cost_rc_m[dc][m]) 
                        for p in suppliers for dc in dcs for m in stores])
fixed_costs = pulp.lpSum([v[dc, m] * vehicle_fixed_cost for dc in dcs for m in stores])

model += var_costs + fixed_costs

# 5. Ограничения:
# Спрос каждого магазина должен быть закрыт
for m in stores:
    model += pulp.lpSum([x[p, dc, m] for p in suppliers for dc in dcs]) == demand[m]
    
# Объем перевозки не может превышать суммарную вместимость нанятых машин
for dc in dcs:
    for m in stores:
        model += pulp.lpSum([x[p, dc, m] for p in suppliers]) <= v[dc, m] * vehicle_cap

# 6. Решение
model.solve(pulp.PULP_CBC_CMD(msg=0))

print(f"Статус решения: {pulp.LpStatus[model.status]}")
print(f"Оптимальные общие затраты (F): {int(pulp.value(model.objective))}\n")

print("Оптимальный путь:")
for p in suppliers:
    for dc in dcs:
        for m in stores:
            if pulp.value(x[p, dc, m]) > 0:
                flow = pulp.value(x[p, dc, m])
                cars = pulp.value(v[dc, m])
                print(f"[{p} -> {dc} -> {m}] | Единиц: {flow} | Нанято машин: {cars}")