import heapq
import math
from services.graph_connection import Neo4jGraphManager  # Cambiamos la importación

# Configuración del manager (debería inicializarse en tu aplicación principal)
neo4j_manager = Neo4jGraphManager(
    "neo4j+s://c547b307.databases.neo4j.io",
    "neo4j",
    "FlX8y9LhsGZdOzn2sPv05t6izI5aB0hiycJCVZQ8r5k"
)

# Variable global para almacenar el grafo en caché
_cached_graph = None
_graph_version = 0

def get_graph(refresh=False):
    global _cached_graph, _graph_version
    if refresh or _cached_graph is None:
        _cached_graph = neo4j_manager.obtener_grafo()  # Usamos el manager
        _graph_version += 1
    return _cached_graph, _graph_version

def invalidate_graph_cache():
    global _cached_graph
    _cached_graph = None

def haversine_heuristic(origin, destination, grafo):
    """Calcula la distancia entre dos ciudades usando la fórmula de Haversine"""
    coord1 = grafo[origin]["coordenadas"]
    coord2 = grafo[destination]["coordenadas"]
    lat1, lon1 = coord1["latitud"], coord1["longitud"]
    lat2, lon2 = coord2["latitud"], coord2["longitud"]

    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    r = 6371  # Radio de la Tierra en km
    return c * r

def a_star_search(origin, destination, grafo):
    """Implementación del algoritmo A*"""
    # Verificar que las ciudades existen en el grafo
    if origin not in grafo or destination not in grafo:
        raise KeyError("Una de las ciudades no existe en el grafo")
    
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
    """Implementación del algoritmo Greedy Best-First Search"""
    if origin not in grafo or destination not in grafo:
        raise KeyError("Una de las ciudades no existe en el grafo")
        
    fringe = []
    heapq.heappush(fringe, (0, origin))
    parent = {origin: None}
    actual_distance = {origin: 0}

    while fringe:
        actual = heapq.heappop(fringe)[1]
        
        if actual == destination:
            break
        
        for next, distance in grafo[actual]["vecinos"].items():
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
        total_distance += grafo[parent[actual]]["vecinos"][actual]
        actual = parent[actual]
    
    route.append(origin)
    route.reverse()
    
    return route, total_distance

def dijkstra_search(origin, destination, grafo):
    """Implementación del algoritmo de Dijkstra"""
    if origin not in grafo or destination not in grafo:
        raise KeyError("Una de las ciudades no existe en el grafo")
        
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
    """Función principal para ejecutar búsquedas"""
    try:
        grafo, _ = get_graph(refresh=True)
        
        # Validar ciudades antes de buscar
        if origin not in grafo:
            raise ValueError(f"Ciudad origen '{origin}' no encontrada")
        if destination not in grafo:
            raise ValueError(f"Ciudad destino '{destination}' no encontrada")
        
        if algorithm == 1:
            return a_star_search(origin, destination, grafo)
        elif algorithm == 2:
            return greedy_search(origin, destination, grafo)
        elif algorithm == 3:
            return dijkstra_search(origin, destination, grafo)
        else:
            raise ValueError("Algoritmo no válido. Use 1 (A*), 2 (Greedy) o 3 (Dijkstra)")
            
    except Exception as e:
        print(f"Error en search_route: {str(e)}")
        raise