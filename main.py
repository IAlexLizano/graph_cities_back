from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import services.search_algorithms as alg
from pydantic import BaseModel
import services.graph_connection as grap

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SearchRequest(BaseModel):
    origen: str
    destino: str



# Endpoint POST
@app.post("/search/{algorithm}")
def search(algorithm: int, data: SearchRequest):
    result = alg.search_route(algorithm, data.origen, data.destino)
    return result    

@app.get("/graph")
def getGraph():
    return grap.grafo

@app.delete("/city/{city_name}")
def eliminar_ciudad(city_name: str):
    if city_name in grap.grafo:
        del grap.grafo[city_name]
        return {"message": f"Ciudad {city_name} eliminada"}
    return {"message": "Ciudad no encontrada"}

@app.post("/city")
def agregar_ciudad(ciudad: dict):
    nombre = ciudad["name"]
    if nombre not in grap.grafo:
        grap.grafo[nombre] = ciudad["vecinos"]
        return {"message": f"Ciudad {nombre} agregada con éxito"}
    return {"message": "Ciudad ya existe"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)