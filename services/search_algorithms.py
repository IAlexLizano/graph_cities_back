import heapq
import math
from services.graph_connection import driver, obtener_grafo

def getGraph():
    with driver.session() as session:
        grafo = session.execute_read(obtener_grafo)
    return grafo

def haversine_heuristic(origin, destination):
    grafo = getGraph()
    #Calcula la distancia entre dos ciudades usando latitud y longitud
    coord1 = grafo[origin]["coordenadas"]
    coord2 = grafo[destination]["coordenadas"]
    lat1, lon1 = coord1["latitud"], coord1["longitud"]
    lat2, lon2 = coord2["latitud"], coord2["longitud"]

    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Haversine
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    r = 6371
    return c * r

def a_star_search(origin, destination):
    grafo = getGraph()
    fringe = []
    heapq.heappush(fringe, (0, origin))
    parent = {origin: None}
    actual_cost = {origin: 0}
    
    while fringe:
        actual = heapq.heappop(fringe)[1]
        
        if actual == destination:
            break
        
        for next, cost in grafo[actual]["vecinos"].items():
            new_cost = actual_cost[actual] + cost
            if next not in actual_cost or new_cost < actual_cost[next]:
                actual_cost[next] = new_cost
                prioridad = new_cost + haversine_heuristic(next, destination)
                heapq.heappush(fringe, (prioridad, next))
                parent[next] = actual

    # Reconstruir el camino
    route = []
    actual = destination
    while actual != origin:
        route.append(actual)
        actual = parent.get(actual)
        if actual is None:
            return [], float('inf')  # No hay camino
    route.append(origin)
    route.reverse()
    
    return route, actual_cost.get(destination, float('inf'))

def greedy_search(origin, destination):
    grafo = getGraph()
    graph = grafo  # Asumo que 'graph' es tu estructura de datos con el grafo
    fringe = []
    heapq.heappush(fringe, (0, origin))
    parent = {origin: None}
    actual_distance = {origin: 0}  # Diccionario para guardar distancias acumuladas

    while fringe:
        actual = heapq.heappop(fringe)[1]
        
        if actual == destination:
            break
        
        for next, distance in graph[actual]["vecinos"].items():
            if next not in parent:
                # Usamos la heurística para la prioridad (como antes)
                priority = haversine_heuristic(next, destination)
                heapq.heappush(fringe, (priority, next))
                parent[next] = actual
                # Guardamos la distancia acumulada
                actual_distance[next] = actual_distance[actual] + distance

    # Reconstruir el camino y calcular distancia total
    route = []
    total_distance = 0
    actual = destination
    while actual != origin:
        if actual is None:  # No hay camino
            return []
        route.append(actual)
        # Sumamos la distancia de este paso
        total_distance += graph[parent[actual]]["vecinos"][actual]
        actual = parent[actual]
    
    route.append(origin)
    route.reverse()
    
    return [route, total_distance]

def dijkstra_search(origin, destination):
    grafo = getGraph()
    graph = grafo
    fringe = []
    heapq.heappush(fringe, (0, origin))
    parent = {origin: None}
    actual_cost = {origin: 0}
    
    while fringe:
        actual = heapq.heappop(fringe)[1]
        
        if actual == destination:
            break
        
        for next, cost in graph[actual]["vecinos"].items():
            new_cost = actual_cost[actual] + cost
            if next not in actual_cost or new_cost < actual_cost[next]:
                actual_cost[next] = new_cost
                heapq.heappush(fringe, (new_cost, next))
                parent[next] = actual

    # Reconstruir el camino
    route = []
    actual = destination
    while actual != origin:
        route.append(actual)
        actual = parent.get(actual)
        if actual is None:
            return [], float('inf')  # No hay camino
    route.append(origin)
    route.reverse()
    
    return route, actual_cost.get(destination, float('inf'))

def search_route(algorithm, origin, destination):
    if algorithm == 1:
        return a_star_search(origin, destination)
    elif algorithm == 2:
        return greedy_search(origin, destination)
    else:
        return dijkstra_search(origin, destination)

# Prueba
# print(dijkstra("Ambato", "Quito"))
