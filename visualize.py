import folium
from folium.plugins import PolyLineTextPath
import requests
import polyline

# 1. ТОЧНЫЕ КООРДИНАТЫ ИЗ ТАБЛИЦЫ [Широта, Долгота]
suppliers = {
    "П1": [50.060, 43.240],   # Михайловка
    "П2": [47.635, 43.147]    # Котельниково
}

dcs = {
    "РЦ1": [49.770, 43.662],  # Фролово
    "РЦ2": [48.787, 44.772],  # Волжский (не активен)
    "РЦ3": [48.689, 43.528]   # Калач-на-Дону
}

stores = {
    "М1": [49.950, 43.800],   # Горьковский
    "М2": [49.900, 43.400],   # Арчеда
    "М3": [48.800, 44.750],   # Краснооктябрьский (Волжский)
    "М4": [48.480, 44.760]    # Светлый Яр (оставлен правильный берег)
}

# 2. Точки для ПРИНУДИТЕЛЬНОГО маршрута в Волжский
mandatory_waypoints = [
    [48.7580, 44.7320]  # Оставили только мост через Ахтубу
]

optimal_routes = [
    {"from": "П1", "via": "РЦ1", "to": "М1"},
    {"from": "П1", "via": "РЦ1", "to": "М2"},
    {"from": "П2", "via": "РЦ3", "to": "М3"},
    {"from": "П2", "via": "РЦ3", "to": "М4"}
]

# 3. Функция построения маршрута
def get_route(start, end, waypoints=None):
    all_points = [start]
    if waypoints:
        all_points.extend(waypoints)
    all_points.append(end)
    
    # OSRM принимает координаты в формате [Долгота, Широта]
    coords_str = ";".join([f"{p[1]},{p[0]}" for p in all_points])
    
    # УБРАЛИ continue_straight=true, чтобы вернуть нормальные развороты в тупиках
    url = f"http://router.project-osrm.org/route/v1/driving/{coords_str}?overview=full&geometries=polyline"
        
    try:
        response = requests.get(url, timeout=5).json()
        if response.get('code') == 'Ok':
            lines = response['routes'][0]['geometry']
            return polyline.decode(lines)
    except Exception as e:
        print(f"Ошибка API OSRM: {e}")
    return [start, end]

# 4. Инициализация карты
m = folium.Map(location=[48.8, 44.2], zoom_start=9, tiles="OpenStreetMap")

# 5. Отрисовка маршрутов
for route in optimal_routes:
    p_name, rc_name, m_name = route["from"], route["via"], route["to"]
    
    p_coords = suppliers[p_name]
    rc_coords = dcs[rc_name]
    m_coords = stores[m_name]
    
    # Плечо 1: Поставщик -> РЦ 
    path_p_to_rc = get_route(p_coords, rc_coords)
    line1 = folium.PolyLine(
        locations=path_p_to_rc, color="#1f77b4", weight=4, opacity=0.8,
        tooltip=f"Маршрут: {p_name} ➔ {rc_name}"
    ).add_to(m)
    PolyLineTextPath(line1, '  ►  ', repeat=True, offset=6, attributes={'fill': '#0f4c81', 'font-weight': 'bold', 'font-size': '14px'}).add_to(m)
    
    # Плечо 2: РЦ -> Магазин
    waypoints_for_m3 = mandatory_waypoints if m_name == "М3" else None
    
    path_rc_to_m = get_route(rc_coords, m_coords, waypoints=waypoints_for_m3)
    line2 = folium.PolyLine(
        locations=path_rc_to_m, color="#d62728", weight=3, opacity=0.8,
        tooltip=f"Маршрут: {rc_name} ➔ {m_name}"
    ).add_to(m)
    PolyLineTextPath(line2, '  ►  ', repeat=True, offset=6, attributes={'fill': '#a61c1c', 'font-weight': 'bold', 'font-size': '14px'}).add_to(m)

# 6. Маркеры объектов
for name, coords in suppliers.items():
    real_name = "Михайловка" if name == "П1" else "Котельниково"
    folium.Marker(location=coords, popup=f"<b>Поставщик {name}</b><br>{real_name}", icon=folium.Icon(color="green", icon="home", prefix="fa")).add_to(m)

for name, coords in dcs.items():
    if name == "РЦ1": real_name = "Фролово"
    elif name == "РЦ2": real_name = "Волжский"
    else: real_name = "Калач-на-Дону"
    is_active = any(r["via"] == name for r in optimal_routes)
    icon_color = "blue" if is_active else "lightblue"
    folium.Marker(location=coords, popup=f"<b>РЦ {name}</b><br>{real_name}<br>{'(Активен)' if is_active else '(Не используется)'}", icon=folium.Icon(color=icon_color, icon="cube", prefix="fa")).add_to(m)

for name, coords in stores.items():
    if name == "М1": real_name = "Горьковский"
    elif name == "М2": real_name = "Арчеда"
    elif name == "М3": real_name = "Краснооктябрьский (Волжский)"
    else: real_name = "Светлый Яр"
    folium.Marker(location=coords, popup=f"<b>Магазин {name}</b><br>{real_name}", icon=folium.Icon(color="red", icon="shopping-cart", prefix="fa")).add_to(m)

m.fit_bounds(m.get_bounds())
m.save("optimal_supply_chain_map_final.html")
print("Карта успешно сохранена: optimal_supply_chain_map_final.html")