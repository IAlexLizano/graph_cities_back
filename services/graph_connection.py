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
    return grafo

# def agregar_ciudad_intermedia(tx, ciudad1, ciudad2, nueva_ciudad, distancia1, distancia2, lat, lon):
#     query = """
#     MATCH (a:Ciudad {nombre: $ciudad1})-[r:CONECTADO_A]-(b:Ciudad {nombre: $ciudad2})
#     DELETE r
#     CREATE (nueva:Ciudad {nombre: $nueva_ciudad, latitud: $lat, longitud: $lon})
#     CREATE (a)-[:CONECTADO_A {distancia: $distancia1}]->(nueva),
#            (nueva)-[:CONECTADO_A {distancia: $distancia2}]->(b),
#            (nueva)-[:CONECTADO_A {distancia: $distancia2}]->(a),
#            (b)-[:CONECTADO_A {distancia: $distancia2}]->(nueva)
#     """
#     tx.run(query, ciudad1=ciudad1, ciudad2=ciudad2, nueva_ciudad=nueva_ciudad,
#            distancia1=distancia1, distancia2=distancia2, lat=lat, lon=lon)

# # Eliminar conexión entre dos ciudades intermedias y conectar extremos
# def eliminar_ciudad_intermedia(tx, ciudad_intermedia, ciudad1, ciudad2, nueva_distancia):
#     query = """
#     MATCH (a:Ciudad {nombre: $ciudad1})-[r1:CONECTADO_A]-(c:Ciudad {nombre: $ciudad_intermedia})-[r2:CONECTADO_A]-(b:Ciudad {nombre: $ciudad2})
#     DELETE r1, r2
#     MERGE (a)-[:CONECTADO_A {distancia: $nueva_distancia}]->(b)
#     MERGE (b)-[:CONECTADO_A {distancia: $nueva_distancia}]->(a)
#     """
#     tx.run(query, ciudad1=ciudad1, ciudad2=ciudad2,
#            ciudad_intermedia=ciudad_intermedia, nueva_distancia=nueva_distancia)


# Obtener el grafo desde Neo4j
with driver.session() as session:
    grafo = session.execute_read(obtener_grafo)

driver.close()

