# Graph Cities Backend

## Descripción del Proyecto

Graph Cities Backend es una API REST desarrollada con FastAPI que permite encontrar rutas óptimas entre ciudades utilizando algoritmos de búsqueda en grafos. El sistema utiliza Neo4j como base de datos de grafos para almacenar las ciudades y sus conexiones, implementando tres algoritmos clásicos de búsqueda: A*, Greedy y Dijkstra.

Este proyecto proporciona un backend robusto para aplicaciones que requieren calcular rutas entre ciudades, considerando distancias reales y utilizando coordenadas geográficas (latitud y longitud) para optimizar las búsquedas.

## Características Principales

- **Búsqueda de Rutas**: Encuentra el camino óptimo entre dos ciudades utilizando diferentes algoritmos
- **Algoritmos Implementados**:
  - **A* (A-Star)**: Búsqueda informada que utiliza heurística de distancia haversine
  - **Greedy (Voraz)**: Búsqueda que prioriza la cercanía al destino
  - **Dijkstra**: Encuentra el camino más corto garantizado
- **Heurística Haversine**: Calcula distancias reales entre coordenadas geográficas
- **Visualización del Grafo**: Endpoint para obtener toda la estructura del grafo
- **API REST**: Interfaz HTTP simple y bien documentada
- **CORS Habilitado**: Permite integración con frontends desde cualquier origen

## Tecnologías Utilizadas

- **Python 3.x**: Lenguaje de programación principal
- **FastAPI**: Framework web moderno y rápido para construir APIs
- **Neo4j**: Base de datos de grafos para almacenar ciudades y conexiones
- **Pydantic**: Validación de datos y gestión de esquemas
- **Uvicorn**: Servidor ASGI para ejecutar la aplicación
- **heapq**: Implementación de colas de prioridad para los algoritmos

## Requisitos Previos

- Python 3.7 o superior
- Acceso a una instancia de Neo4j (base de datos de grafos)
- pip (gestor de paquetes de Python)

## Instalación

1. **Clonar el repositorio**:
```bash
git clone <url-del-repositorio>
cd graph_cities_back
```

2. **Instalar las dependencias**:
```bash
pip install fastapi uvicorn neo4j pydantic
```

Alternativamente, si existe un archivo `requirements.txt`:
```bash
pip install -r requirements.txt
```

## Configuración

### Configurar Conexión a Neo4j

Edita el archivo `services/graph_connection.py` y actualiza las credenciales de tu base de datos Neo4j:

```python
URI = "neo4j+s://tu-instancia.databases.neo4j.io"
USER = "neo4j"
PASSWORD = "tu-contraseña"
```

### Estructura de Datos en Neo4j

Las ciudades deben estar almacenadas en Neo4j con la siguiente estructura:

```cypher
// Nodo Ciudad
(:Ciudad {
    nombre: "NombreCiudad",
    latitud: -0.1234,
    longitud: -78.5678
})

// Relación CONECTADO_A
(:Ciudad)-[:CONECTADO_A {distancia: 120.5}]->(:Ciudad)
```

## Uso

### Iniciar el Servidor

Ejecuta el siguiente comando para iniciar el servidor de desarrollo:

```bash
python main.py
```

O usando uvicorn directamente:

```bash
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

El servidor estará disponible en: `http://127.0.0.1:8000`

### Documentación Interactiva

FastAPI proporciona documentación automática e interactiva:

- **Swagger UI**: `http://127.0.0.1:8000/docs`
- **ReDoc**: `http://127.0.0.1:8000/redoc`

## Endpoints de la API

### 1. Buscar Ruta

**POST** `/search/{algorithm}`

Busca una ruta entre dos ciudades utilizando el algoritmo especificado.

**Parámetros de URL**:
- `algorithm` (int): Identificador del algoritmo
  - `1`: A* (A-Star)
  - `2`: Greedy (Voraz)
  - `3`: Dijkstra

**Cuerpo de la Petición**:
```json
{
  "origen": "Quito",
  "destino": "Guayaquil"
}
```

**Respuesta de Ejemplo**:
```json
[
  ["Quito", "Ambato", "Riobamba", "Guayaquil"],
  450.5
]
```

**Ejemplo de uso con curl**:
```bash
curl -X POST "http://127.0.0.1:8000/search/1" \
  -H "Content-Type: application/json" \
  -d '{"origen":"Quito","destino":"Guayaquil"}'
```

### 2. Obtener Grafo

**GET** `/graph`

Retorna la estructura completa del grafo con todas las ciudades y sus conexiones.

**Respuesta de Ejemplo**:
```json
{
  "Quito": {
    "coordenadas": {
      "latitud": -0.1807,
      "longitud": -78.4678
    },
    "vecinos": {
      "Ambato": 120.5,
      "Latacunga": 89.3
    }
  },
  "Ambato": {
    "coordenadas": {
      "latitud": -1.2490,
      "longitud": -78.6167
    },
    "vecinos": {
      "Quito": 120.5,
      "Riobamba": 52.0
    }
  }
}
```

**Ejemplo de uso con curl**:
```bash
curl http://127.0.0.1:8000/graph
```

## Algoritmos de Búsqueda

### A* (A-Star)

Combina el costo real del camino con una heurística (distancia haversine) para encontrar la ruta óptima de manera eficiente. Es ideal cuando se conocen las coordenadas geográficas.

**Ventajas**:
- Encuentra el camino óptimo
- Más eficiente que Dijkstra gracias a la heurística
- Utiliza información geográfica para priorizar búsquedas

### Greedy (Voraz)

Selecciona siempre el siguiente nodo más cercano al destino según la heurística. Es rápido pero no garantiza el camino óptimo.

**Ventajas**:
- Muy rápido
- Usa poca memoria
- Bueno para aproximaciones rápidas

**Desventajas**:
- No garantiza el camino óptimo

### Dijkstra

Explora todos los caminos posibles para garantizar encontrar el camino más corto. No utiliza heurística.

**Ventajas**:
- Garantiza encontrar el camino más corto
- Funciona sin necesidad de coordenadas geográficas

**Desventajas**:
- Más lento que A* cuando hay heurística disponible
- Explora más nodos innecesarios

## Estructura del Proyecto

```
graph_cities_back/
│
├── main.py                          # Punto de entrada de la aplicación
│   ├── Configuración de FastAPI
│   ├── Middleware CORS
│   ├── Modelos Pydantic
│   └── Definición de endpoints
│
├── services/
│   ├── graph_connection.py         # Conexión y obtención de datos desde Neo4j
│   │   ├── Configuración de Neo4j
│   │   ├── Función obtener_grafo()
│   │   └── Construcción de la estructura del grafo
│   │
│   └── search_algorithms.py        # Implementación de algoritmos de búsqueda
│       ├── haversine_heuristic()   # Cálculo de distancia geográfica
│       ├── a_star_search()         # Algoritmo A*
│       ├── greedy_search()         # Algoritmo Greedy
│       ├── dijkstra_search()       # Algoritmo Dijkstra
│       └── search_route()          # Selector de algoritmo
│
└── .gitignore                       # Archivos ignorados por git
```

## Componentes Principales

### main.py

Archivo principal que:
- Inicializa la aplicación FastAPI
- Configura CORS para permitir peticiones desde cualquier origen
- Define el modelo de datos `SearchRequest`
- Expone los endpoints REST
- Configura el servidor Uvicorn

### services/graph_connection.py

Módulo responsable de:
- Establecer conexión con Neo4j
- Ejecutar consultas Cypher para obtener ciudades y conexiones
- Construir la estructura de datos del grafo en Python
- Incluir coordenadas geográficas para cada ciudad

### services/search_algorithms.py

Módulo que implementa:
- **haversine_heuristic()**: Calcula la distancia en línea recta entre dos puntos usando la fórmula de Haversine
- **a_star_search()**: Búsqueda A* con heurística
- **greedy_search()**: Búsqueda voraz basada en heurística
- **dijkstra_search()**: Búsqueda del camino más corto garantizado
- **search_route()**: Función dispatcher que selecciona el algoritmo a usar

## Modelo de Datos

### SearchRequest

```python
class SearchRequest(BaseModel):
    origen: str      # Nombre de la ciudad de origen
    destino: str     # Nombre de la ciudad de destino
```

### Estructura del Grafo

```python
{
    "NombreCiudad": {
        "coordenadas": {
            "latitud": float,
            "longitud": float
        },
        "vecinos": {
            "CiudadVecina1": distancia_float,
            "CiudadVecina2": distancia_float
        }
    }
}
```

## Fórmula Haversine

La función `haversine_heuristic` utiliza la fórmula de Haversine para calcular la distancia entre dos puntos en la superficie de una esfera:

```
a = sin²(Δlat/2) + cos(lat1) × cos(lat2) × sin²(Δlon/2)
c = 2 × arcsin(√a)
d = R × c
```

Donde:
- `R` = 6371 km (radio de la Tierra)
- `Δlat` = diferencia de latitudes
- `Δlon` = diferencia de longitudes

## Ejemplos de Uso

### Ejemplo con Python requests

```python
import requests

# Buscar ruta usando A*
url = "http://127.0.0.1:8000/search/1"
data = {
    "origen": "Quito",
    "destino": "Cuenca"
}

response = requests.post(url, json=data)
ruta, distancia = response.json()

print(f"Ruta encontrada: {' -> '.join(ruta)}")
print(f"Distancia total: {distancia} km")
```

### Ejemplo con JavaScript (Fetch API)

```javascript
// Buscar ruta usando Dijkstra
fetch('http://127.0.0.1:8000/search/3', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        origen: 'Quito',
        destino: 'Guayaquil'
    })
})
.then(response => response.json())
.then(data => {
    const [ruta, distancia] = data;
    console.log('Ruta:', ruta.join(' -> '));
    console.log('Distancia:', distancia, 'km');
});
```

## Consideraciones de Seguridad

⚠️ **IMPORTANTE**: El archivo `services/graph_connection.py` contiene credenciales de Neo4j en texto plano. Para ambientes de producción:

1. **Usar variables de entorno**:
```python
import os
URI = os.getenv("NEO4J_URI")
USER = os.getenv("NEO4J_USER")
PASSWORD = os.getenv("NEO4J_PASSWORD")
```

2. **Archivo .env** (no commitearlo):
```
NEO4J_URI=neo4j+s://tu-instancia.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=tu-contraseña-segura
```

3. **Usar python-dotenv** para cargar variables:
```bash
pip install python-dotenv
```

```python
from dotenv import load_dotenv
load_dotenv()
```

## Mejoras Futuras

- [ ] Implementar autenticación y autorización
- [ ] Agregar tests unitarios y de integración
- [ ] Crear archivo `requirements.txt` con todas las dependencias
- [ ] Mover credenciales a variables de entorno
- [ ] Agregar logging estructurado
- [ ] Implementar caché para consultas frecuentes
- [ ] Agregar validación de existencia de ciudades
- [ ] Implementar rate limiting
- [ ] Agregar métricas y monitoreo
- [ ] Dockerizar la aplicación

## Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## Licencia

Este proyecto está bajo la licencia que especifique el propietario del repositorio.

## Contacto

Para preguntas o sugerencias sobre el proyecto, por favor abre un issue en el repositorio.

---

**Desarrollado con ❤️ usando FastAPI y Neo4j**
