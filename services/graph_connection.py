from neo4j import GraphDatabase
import threading

class GraphManager:
    def __init__(self, uri, user, password):
        self._driver = GraphDatabase.driver(
            uri,
            auth=(user, password),
            max_connection_lifetime=1800,
            connection_timeout=15,
            keep_alive=True,
        )
        self._lock = threading.Lock()

    def close(self):
        """Cierra la conexión con la base de datos"""
        if self._driver:
            self._driver.close()

    def _execute_read(self, tx_func, **kwargs):
        """Ejecuta una operación de lectura"""
        with self._driver.session() as session:
            return session.execute_read(tx_func, **kwargs)

    def _execute_write(self, tx_func, **kwargs):
        """Ejecuta una operación de escritura"""
        with self._driver.session() as session:
            return session.execute_write(tx_func, **kwargs)

    def obtain_graph(self):
        """Obtiene todo el grafo de ciudades y conexiones"""
        with self._lock:
            return self._execute_read(self._tx_obtain_graph)

    @staticmethod
    def _tx_obtain_graph(tx):
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

    def exists_city(self, nombre_ciudad):
        """Verifica si una ciudad existe"""
        with self._lock:
            return self._execute_read(self._tx_exists_city, nombre=nombre_ciudad)

    @staticmethod
    def _tx_exists_city(tx, nombre):
        query = "MATCH (c:Ciudad {nombre: $nombre}) RETURN count(c) > 0 AS existe"
        result = tx.run(query, nombre=nombre)
        return result.single()["existe"]

    def add_intermediate(self, ciudad1, ciudad2, nueva_ciudad, distancia1, lat, lon):
        """Agrega una ciudad intermedia entre dos ciudades existentes"""
        with self._lock:
            return self._execute_write(
                self._tx_add_intermediate,
                ciudad1=ciudad1,
                ciudad2=ciudad2,
                nueva_ciudad=nueva_ciudad,
                distancia1=distancia1,
                lat=lat,
                lon=lon
            )

    @staticmethod
    def _tx_add_intermediate(tx, ciudad1, ciudad2, nueva_ciudad, distancia1, lat, lon):
        query = """
        MATCH (a:Ciudad {nombre: $ciudad1})-[r:CONECTADO_A]-(b:Ciudad {nombre: $ciudad2})
        WITH a, b, r, r.distancia AS distancia_total
        WHERE $distancia1 < distancia_total
        
        MERGE (nueva:Ciudad {nombre: $nueva_ciudad})
        ON CREATE SET nueva.latitud = $lat, nueva.longitud = $lon
        
        DELETE r
        
        MERGE (a)-[:CONECTADO_A {distancia: $distancia1}]->(nueva)
        MERGE (nueva)-[:CONECTADO_A {distancia: $distancia1}]->(a)
        MERGE (nueva)-[:CONECTADO_A {distancia: distancia_total - $distancia1}]->(b)
        MERGE (b)-[:CONECTADO_A {distancia: distancia_total - $distancia1}]->(nueva)
        
        RETURN true AS exito
        """
        
        params = {
            'ciudad1': ciudad1,
            'ciudad2': ciudad2,
            'nueva_ciudad': nueva_ciudad,
            'distancia1': distancia1,
            'lat': lat,
            'lon': lon
        }
        
        result = tx.run(query, parameters=params)
        return result.single()["exito"]

    def delete_intermediate(self, intermedia, ciudad1, ciudad2):
        """Elimina una ciudad intermedia y reconecta las ciudades originales"""
        with self._lock:
            return self._execute_write(
                self._tx_delete_intermediate,
                intermedia=intermedia,
                ciudad1=ciudad1,
                ciudad2=ciudad2
            )

    @staticmethod
    def _tx_delete_intermediate(tx, intermedia, ciudad1, ciudad2):
        query = """
        MATCH (a:Ciudad {nombre: $ciudad1})-[r1:CONECTADO_A]-(c:Ciudad {nombre: $intermedia})-[r2:CONECTADO_A]-(b:Ciudad {nombre: $ciudad2})
        WITH a, b, c, r1, r2, r1.distancia + r2.distancia AS nueva_distancia
        
        MERGE (a)-[nueva1:CONECTADO_A]->(b)
        SET nueva1.distancia = nueva_distancia
        
        MERGE (b)-[nueva2:CONECTADO_A]->(a)
        SET nueva2.distancia = nueva_distancia
        
        DELETE r1, r2
        
        RETURN true AS exito
        """
        
        params = {
            'intermedia': intermedia,
            'ciudad1': ciudad1,
            'ciudad2': ciudad2
        }
        
        result = tx.run(query, parameters=params)
        return result.single()["exito"]

    def add_city(self, ciudad_existente, nueva_ciudad, distancia, lat, lon):
        """Agrega una nueva ciudad conectada a una existente"""
        with self._lock:
            return self._execute_write(
                self._tx_add_city,
                ciudad_existente=ciudad_existente,
                nueva_ciudad=nueva_ciudad,
                distancia=distancia,
                lat=lat,
                lon=lon
            )

    @staticmethod
    def _tx_add_city(tx, ciudad_existente, nueva_ciudad, distancia, lat, lon):
        query = """
        MATCH (existente:Ciudad {nombre: $ciudad_existente})
        CREATE (nueva:Ciudad {nombre: $nueva_ciudad, latitud: $lat, longitud: $lon})
        CREATE (existente)-[:CONECTADO_A {distancia: $distancia}]->(nueva)
        CREATE (nueva)-[:CONECTADO_A {distancia: $distancia}]->(existente)
        RETURN true AS exito
        """
        params = {
            'ciudad_existente': ciudad_existente,
            'nueva_ciudad': nueva_ciudad,
            'distancia': distancia,
            'lat': lat,
            'lon': lon
        }
        
        result = tx.run(query, parameters=params)
        return result.single()["exito"]

    def add_route(self, ciudad1, ciudad2, distancia):
        """Conecta dos ciudades existentes con una distancia dada"""
        with self._lock:
            return self._execute_write(
                self._tx_add_route,
                ciudad1=ciudad1,
                ciudad2=ciudad2,
                distancia=distancia
            )

    @staticmethod
    def _tx_add_route(tx, ciudad1, ciudad2, distancia):
        query = """
        MATCH (a:Ciudad {nombre: $ciudad1})
        MATCH (b:Ciudad {nombre: $ciudad2})
        WHERE a <> b
        
        MERGE (a)-[r1:CONECTADO_A]->(b)
        SET r1.distancia = $distancia
        
        MERGE (b)-[r2:CONECTADO_A]->(a)
        SET r2.distancia = $distancia
        
        RETURN true AS exito
        """
        
        params = {
            'ciudad1': ciudad1,
            'ciudad2': ciudad2,
            'distancia': distancia,
        }
        
        result = tx.run(query, parameters= params)
        return result.single()["exito"]

    def delete_city(self, nombre_ciudad):
        """Elimina una ciudad y todas sus relaciones"""
        with self._lock:
            return self._execute_write(self._tx_delete_city, nombre=nombre_ciudad)

    @staticmethod
    def _tx_delete_city(tx, nombre):
        query = """
        MATCH (c:Ciudad {nombre: $nombre})
        OPTIONAL MATCH (c)-[r]-()
        DELETE r, c
        RETURN count(c) > 0 AS eliminado
        """
        result = tx.run(query, nombre=nombre)
        return result.single()["eliminado"]

    def delete_route(self, ciudad1, ciudad2):
        """Elimina la conexión directa entre dos ciudades"""
        with self._lock:
            return self._execute_write(
                self._tx_delete_route,
                ciudad1=ciudad1,
                ciudad2=ciudad2
            )

    @staticmethod
    def _tx_delete_route(tx, ciudad1, ciudad2):
        query = """
        MATCH (a:Ciudad {nombre: $ciudad1})-[r:CONECTADO_A]-(b:Ciudad {nombre: $ciudad2})
        DELETE r
        RETURN count(r) > 0 AS eliminada
        """
        params = {
            'ciudad1': ciudad1,
            'ciudad2': ciudad2,
        }
        
        result = tx.run(query, parameters= params)
        return result.single()["eliminada"]

    def __del__(self):
        """Destructor que cierra la conexión"""
        self.close()

driver = GraphManager(
    "neo4j+s://c547b307.databases.neo4j.io",
    "neo4j",
    "FlX8y9LhsGZdOzn2sPv05t6izI5aB0hiycJCVZQ8r5k"
)