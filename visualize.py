import folium
from folium.plugins import PolyLineTextPath
import requests
import polyline
import math

# 1. Координаты [Широта, Долгота]
warehouses = {
    "Склад 1": [48.835196, 44.647806],
    "Склад 2": [48.723019, 44.871980]
}

stores = {
    "Магнит Семейный 1": [48.808140, 44.612455],
    "Магнит Экстра 1": [48.811485, 44.732980],
    "Магнит Экстра 2": [48.783400, 44.780400],
    "Магнит Семейный 2": [48.773700, 44.783600]
}

# Результаты решения (объемы)
optimal_routes = [
    {"Откуда": "Склад 1", "Куда": "Магнит Семейный 1", "Объем": 40},
    {"Откуда": "Склад 1", "Куда": "Магнит Экстра 1", "Объем": 70},
    {"Откуда": "Склад 1", "Куда": "Магнит Экстра 2", "Объем": 20},
    {"Откуда": "Склад 2", "Куда": "Магнит Экстра 2", "Объем": 40},
    {"Откуда": "Склад 2", "Куда": "Магнит Семейный 2", "Объем": 50}
]

# Цвета для сетей
colors = {"Склад 1": "green", "Склад 2": "purple"}

# Создаем карту
m = folium.Map(location=[48.78, 44.72], zoom_start=12)

def get_route(start, end):
    """Получает геометрию дороги. Если сервер упал — возвращает прямую линию."""
    try:
        # ВАЖНО: OSRM ждет [Долгота, Широта]
        url = f"http://router.project-osrm.org/route/v1/driving/{start[1]},{start[0]};{end[1]},{end[0]}?overview=full"
        r = requests.get(url, timeout=5).json()
        if r.get("code") == "Ok":
            return polyline.decode(r["routes"][0]["geometry"])
    except Exception as e:
        print(f"Ошибка API OSRM: {e}")
    # Если API не сработало, рисуем прямую (для отладки)
    return [start, end]

# Рисуем пути
for route in optimal_routes:
    s_name, st_name = route["Откуда"], route["Куда"]
    path = get_route(warehouses[s_name], stores[st_name])
    
    if path:
        # 1. Рисуем основную линию
        line_color = colors.get(s_name, "blue")
        line_weight = max(3, route["Объем"] / 10)
        
        main_line = folium.PolyLine(
            locations=path,
            color=line_color,
            weight=line_weight,
            opacity=0.7,
            tooltip=f"{s_name} -> {st_name} ({route['Объем']} паллет)"
        ).add_to(m)
        
        # 2. ДОБАВЛЯЕМ СТРЕЛКИ (Плагин PolyLineTextPath)
        # Он рисует символ треугольника вдоль всей линии
        PolyLineTextPath(
            main_line,
            '  ►  ', # Символ стрелки
            repeat=True,
            offset=7, # Смещение от центра линии
            attributes={'fill': 'white', 'font-weight': 'bold', 'font-size': '18px'}
        ).add_to(m)

# Ставим маркеры (упростим для надежности)
for name, coords in warehouses.items():
    folium.Marker(coords, popup=name, icon=folium.Icon(color='red', icon='cloud')).add_to(m)

for name, coords in stores.items():
    folium.Marker(coords, popup=name, icon=folium.Icon(color='blue', icon='shopping-cart')).add_to(m)

# Автоматически подбираем масштаб, чтобы все влезло
m.fit_bounds(m.get_bounds())

m.save("map_with_arrows.html")
print("Карта сохранена в файл map_with_arrows.html")