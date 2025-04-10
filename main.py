from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import services.search_algorithms as alg
from pydantic import BaseModel
from services.graph_connection import GraphManager

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicialización del manager Neo4j
neo4j_mgr = GraphManager(
    "neo4j+s://c547b307.databases.neo4j.io",
    "neo4j",
    "FlX8y9LhsGZdOzn2sPv05t6izI5aB0hiycJCVZQ8r5k"
)

# Modelos Pydantic
class SearchRequest(BaseModel):
    origen: str
    destino: str

class AddIntermediateRequest(BaseModel):
    ciudad1: str
    ciudad2: str
    nueva: str
    distancia1: float
    latitud: float
    longitud: float

class DeleteIntermediateRequest(BaseModel):
    intermedia: str
    ciudad1: str
    ciudad2: str

class AddNodeRequest(BaseModel):
    ciudad_existente: str
    nueva_ciudad: str
    distancia: float
    latitud: float
    longitud: float

class AddRelationshipRequest(BaseModel):
    ciudad1: str
    ciudad2: str
    distancia: float

class DeleteNodeRequest(BaseModel):
    nombre_ciudad: str

class DeleteRelationshipRequest(BaseModel):
    ciudad1: str
    ciudad2: str

# Endpoints
@app.post("/search/{algorithm}")
async def search_route(algorithm: int, data: SearchRequest):
    try:
        grafo, _ = alg.get_graph()
        if data.origen not in grafo or data.destino not in grafo:
            raise KeyError("Una de las ciudades no existe en el grafo")
            
        result = alg.search_route(algorithm, data.origen, data.destino)
        return result
    except KeyError as e:
        raise HTTPException(status_code=404, detail=f"Ciudad no encontrada: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/graph")
async def get_graph():
    try:
        grafo = neo4j_mgr.obtain_graph()
        return grafo
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/graph/add-intermediate")
async def add_intermediate_city(data: AddIntermediateRequest):
    try:
        if not neo4j_mgr.exists_city(data.ciudad1) or not neo4j_mgr.exists_city(data.ciudad2):
            raise HTTPException(status_code=404, detail="Una de las ciudades no existe")
            
        success = neo4j_mgr.add_intermediate(
            data.ciudad1,
            data.ciudad2,
            data.nueva,
            data.distancia1,
            data.latitud,
            data.longitud
        )
        if not success:
            raise HTTPException(status_code=400, detail="No se pudo agregar la ciudad intermedia")
            
        alg.invalidate_graph_cache()
        return {"success": True, "message": f"{data.nueva} agregada entre {data.ciudad1} y {data.ciudad2}"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/graph/delete-intermediate")
async def delete_intermediate_city(data: DeleteIntermediateRequest):
    try:
        success = neo4j_mgr.delete_intermediate(
            data.intermedia,
            data.ciudad1,
            data.ciudad2
        )
        if success:
            alg.invalidate_graph_cache()
            return {"success": True, "message": f"{data.intermedia} eliminada y {data.ciudad1} reconectada con {data.ciudad2}"}
        raise HTTPException(status_code=400, detail="No se pudo eliminar la ciudad intermedia")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/graph/add-node")
async def add_city_node(data: AddNodeRequest):
    try:
        success = neo4j_mgr.add_city(
            data.ciudad_existente,
            data.nueva_ciudad,
            data.distancia,
            data.latitud,
            data.longitud
        )
        if success:
            alg.invalidate_graph_cache()
            return {"success": True, "message": f"{data.nueva_ciudad} agregada y conectada a {data.ciudad_existente}"}
        raise HTTPException(status_code=400, detail="No se pudo agregar la nueva ciudad")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/graph/add-relationship")
async def add_city_relationship(data: AddRelationshipRequest):
    try:
        success = neo4j_mgr.add_route(
            data.ciudad1,
            data.ciudad2,
            data.distancia
        )
        if success:
            alg.invalidate_graph_cache()
            return {"success": True, "message": f"Conexión agregada entre {data.ciudad1} y {data.ciudad2}"}
        raise HTTPException(status_code=400, detail="No se pudo agregar la relación")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/graph/delete-node")
async def delete_city_node(data: DeleteNodeRequest):
    try:
        success = neo4j_mgr.delete_city(data.nombre_ciudad)
        if success:
            alg.invalidate_graph_cache()
            return {"success": True, "message": f"{data.nombre_ciudad} eliminada del grafo"}
        raise HTTPException(status_code=400, detail="No se pudo eliminar la ciudad")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/graph/delete-relationship")
async def delete_city_relationship(data: DeleteRelationshipRequest):
    try:
        success = neo4j_mgr.delete_route(data.ciudad1, data.ciudad2)
        if success:
            alg.invalidate_graph_cache()
            return {"success": True, "message": f"Conexión eliminada entre {data.ciudad1} y {data.ciudad2}"}
        raise HTTPException(status_code=400, detail="No se pudo eliminar la relación")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)