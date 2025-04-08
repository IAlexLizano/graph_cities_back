import heapq
import math
from services.graph_connection import driver, obtener_grafo

# Variable global para almacenar el grafo en caché
_cached_graph = None
_graph_version = 0

def get_graph(refresh=False):
    global _cached_graph, _graph_version
    if refresh or _cached_graph is None:
        with driver.session() as session:
            _cached_graph = session.execute_read(obtener_grafo)
        _graph_version += 1
        driver.close()
    return _cached_graph, _graph_version

def invalidate_graph_cache():
    global _cached_graph
    _cached_graph = None

def haversine_heuristic(origin, destination, grafo):
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

def a_star_search(origin, destination, grafo):
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
                prioridad = new_cost + haversine_heuristic(next, destination, grafo)
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

def greedy_search(origin, destination, grafo):
    graph = grafo
    fringe = []
    heapq.heappush(fringe, (0, origin))
    parent = {origin: None}
    actual_distance = {origin: 0}

    while fringe:
        actual = heapq.heappop(fringe)[1]
        
        if actual == destination:
            break
        
        for next, distance in graph[actual]["vecinos"].items():
            if next not in parent:
                priority = haversine_heuristic(next, destination, grafo)
                heapq.heappush(fringe, (priority, next))
                parent[next] = actual
                actual_distance[next] = actual_distance[actual] + distance

    # Reconstruir el camino y calcular distancia total
    route = []
    total_distance = 0
    actual = destination
    while actual != origin:
        if actual is None:  # No hay camino
            return []
        route.append(actual)
        total_distance += graph[parent[actual]]["vecinos"][actual]
        actual = parent[actual]
    
    route.append(origin)
    route.reverse()
    
    return [route, total_distance]

def dijkstra_search(origin, destination, grafo):
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
    grafo, _ = get_graph()
    if algorithm == 1:
        return a_star_search(origin, destination, grafo)
    elif algorithm == 2:
        return greedy_search(origin, destination, grafo)
    else:
        return dijkstra_search(origin, destination, grafo)