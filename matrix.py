import requests
import pandas as pd

# 1. Подготовка данных (Координаты в формате: Longitude, Latitude)
warehouses = {
    "Склад 1": [44.647806, 48.835196],
    "Склад 2": [44.871980, 48.723019]
}

stores = {
    "Магнит Семейный 1": [44.612455, 48.808140],
    "Магнит Экстра 1": [44.732980, 48.811485],
    "Магнит Экстра 2": [44.780400, 48.783400],
    "Магнит Семейный 2": [44.783600, 48.773700]
}

def get_distance_matrix(sources, destinations):
    # Формируем строку координат для OSRM: сначала все склады, потом все магазины
    all_coords = list(sources.values()) + list(destinations.values())
    coords_str = ";".join([f"{c[0]},{c[1]}" for c in all_coords])
    
    # Индексы источников (складов) и пунктов назначения (магазинов) в общем списке
    src_indices = ";".join([str(i) for i in range(len(sources))])
    dst_indices = ";".join([str(i) for i in range(len(sources), len(sources) + len(destinations))])
    
    # Запрос к публичному демо-серверу OSRM (Table service)
    url = f"http://router.project-osrm.org/table/v1/driving/{coords_str}?sources={src_indices}&destinations={dst_indices}&annotations=distance"
    
    response = requests.get(url).json()
    
    # Извлекаем дистанции (переводим метры в километры)
    distances = [[round(d / 1000, 2) for d in row] for row in response['distances']]
    
    # Оформляем в виде таблицы (DataFrame)
    df = pd.DataFrame(distances, index=sources.keys(), columns=destinations.keys())
    return df

# Выполняем расчет
matrix = get_distance_matrix(warehouses, stores)

print("Матрица расстояний (в км):")
print(matrix)