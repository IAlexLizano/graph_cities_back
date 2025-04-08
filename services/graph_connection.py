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
    // Verificar si la conexión original existe
    OPTIONAL MATCH (a:Ciudad {nombre: $ciudad1})-[r1:CONECTADO_A]-(b:Ciudad {nombre: $ciudad2})
    WITH a, b, r1, 
         CASE WHEN r1 IS NOT NULL THEN r1.distancia ELSE 0 END AS distancia_total,
         $distancia1 AS distancia_nueva
    
    // Validar que ambas ciudades existan y la distancia sea válida
    WHERE a IS NOT NULL AND b IS NOT NULL AND 
          (r1 IS NULL OR distancia_nueva <= distancia_total)
    
    // Crear o encontrar la nueva ciudad (solo establece coordenadas si es nueva)
    MERGE (nueva:Ciudad {nombre: $nueva_ciudad})
    ON CREATE SET nueva.latitud = $lat, nueva.longitud = $lon
    
    // Si existía una conexión original, eliminarla
    DELETE r1
    
    // Crear conexiones con la nueva ciudad (o actualizar si ya existían)
    MERGE (a)-[r_a_nueva:CONECTADO_A]->(nueva)
    SET r_a_nueva.distancia = $distancia1
    MERGE (nueva)-[r_nueva_a:CONECTADO_A]->(a)
    SET r_nueva_a.distancia = $distancia1
    
    // Calcular distancia restante (si había conexión original)
    WITH a, b, nueva, distancia_total, distancia_nueva,
         CASE WHEN distancia_total > 0 
              THEN distancia_total - distancia_nueva 
              ELSE $distancia1 END AS distancia_restante
    
    // Crear conexiones con la otra ciudad
    MERGE (b)-[r_b_nueva:CONECTADO_A]->(nueva)
    SET r_b_nueva.distancia = distancia_restante
    MERGE (nueva)-[r_nueva_b:CONECTADO_A]->(b)
    SET r_nueva_b.distancia = distancia_restante
    
    RETURN true AS exito, 
           CASE WHEN distancia_total > 0 
                THEN 'Conexión actualizada' 
                ELSE 'Nueva conexión creada' END AS mensaje
    """
    try:
        result = tx.run(query, ciudad1=ciudad1, ciudad2=ciudad2, nueva_ciudad=nueva_ciudad,
                       distancia1=distancia1, lat=lat, lon=lon)
        record = result.single()
        print(result)
        if record:
            return record["exito"], record["mensaje"]
        return False, "No se encontraron las ciudades especificadas"
    except Exception as e:
        return False, f"Error: {str(e)}"

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

