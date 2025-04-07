from neo4j import GraphDatabase

URI = "neo4j+s://c547b307.databases.neo4j.io"
USER = "neo4j"
PASSWORD = "FlX8y9LhsGZdOzn2sPv05t6izI5aB0hiycJCVZQ8r5k"

# Crear conexión con Neo4j
driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))

# Obtener los datos desde Neo4j
def obtener_grafo(tx):
    query = """
    MATCH (a:Ciudad)-[r:CONECTADO_A]-(b:Ciudad)
    RETURN a.nombre AS origen, 
        b.nombre AS destino, 
        r.distancia AS distancia,
        a.latitud AS origen_latitud,
        a.longitud AS origen_longitud,
        b.latitud AS destino_latitud,
        b.longitud AS destino_longitud
    ORDER BY origen ASC
    """
    result = tx.run(query)

    grafo = {}
    for record in result:
        origen = record["origen"]
        destino = record["destino"]
        distancia = record["distancia"]
        origen_lat = record["origen_latitud"]
        origen_lon = record["origen_longitud"]
        destino_lat = record["destino_latitud"]
        destino_lon = record["destino_longitud"]

        if origen not in grafo:
            grafo[origen] = {
                "coordenadas": {"latitud": origen_lat, "longitud": origen_lon},
                "vecinos": {}
            }
        if destino not in grafo:
            grafo[destino] = {
                "coordenadas": {"latitud": destino_lat, "longitud": destino_lon},
                "vecinos": {}
            }

        grafo[origen]["vecinos"][destino] = distancia
    return dict(sorted(grafo.items()))

def agregar_ciudad(tx, ciudad1, ciudad2, nueva_ciudad, distancia1, lat, lon):
    query = """
    MATCH (a:Ciudad {nombre: $ciudad1})-[r1:CONECTADO_A]-(b:Ciudad {nombre: $ciudad2})
    // Llevamos la relación completa (r1) en el WITH, no solo su distancia
    WITH a, b, r1, r1.distancia AS distancia_original
    WITH a, b, r1, distancia_original, $distancia1 AS distancia_nueva
    WITH a, b, r1, distancia_original, distancia_nueva, distancia_original - distancia_nueva AS distancia_restante
    // Ahora podemos eliminar r1 porque la mantenemos en el WITH
    DELETE r1
    // Crear la nueva ciudad
    CREATE (nueva:Ciudad {nombre: $nueva_ciudad, latitud: $lat, longitud: $lon})
    // Crear las nuevas relaciones
    CREATE (nueva)-[:CONECTADO_A {distancia: distancia_restante}]->(b)
    CREATE (nueva)-[:CONECTADO_A {distancia: distancia_nueva}]->(a)
    """
    tx.run(query, ciudad1=ciudad1, ciudad2=ciudad2, nueva_ciudad=nueva_ciudad,
           distancia1=distancia1, lat=lat, lon=lon)

def eliminar_ciudad(tx, ciudad_intermedia, ciudad1, ciudad2):
    query = """
    MATCH (a:Ciudad {nombre: $ciudad1})-[r1:CONECTADO_A]-(c:Ciudad {nombre: $ciudad_intermedia})-[r2:CONECTADO_A]-(b:Ciudad {nombre: $ciudad2})
    WITH a, b, c, r1, r2, r1.distancia + r2.distancia AS nueva_distancia

    MERGE (a)-[r_nuevo1:CONECTADO_A]->(b)
    SET r_nuevo1.distancia = nueva_distancia

    MERGE (b)-[r_nuevo2:CONECTADO_A]->(a)
    SET r_nuevo2.distancia = nueva_distancia

    WITH a, b, c  // Necesario para seguir usando estas variables después
    MATCH (a)-[r1_old:CONECTADO_A]-(c)-[r2_old:CONECTADO_A]-(b)
    DELETE r1_old, r2_old
    """
    tx.run(query, ciudad1=ciudad1, ciudad2=ciudad2, ciudad_intermedia=ciudad_intermedia)

