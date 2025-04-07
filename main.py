from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import services.search_algorithms as alg
from pydantic import BaseModel
from services.graph_connection import driver, agregar_ciudad, eliminar_ciudad, obtener_grafo


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

class AddRequest(BaseModel):
    ciudad1: str
    ciudad2: str
    nueva: str
    distancia1: float
    latitud: float
    longitud: float

class DeleteRequest(BaseModel):
    intermedia: str
    ciudad1: str
    ciudad2: str

# Endpoint POST
@app.post("/search/{algorithm}")
def search(algorithm: int, data: SearchRequest):
    result = alg.search_route(algorithm, data.origen, data.destino)
    return result    

@app.get("/graph")
def getGraph():
    with driver.session() as session:
        grafo = session.execute_read(obtener_grafo)
    return grafo

@app.post("/graph/add-city")
def agregar_intermedia(data: AddRequest):
    with driver.session() as session:
        session.execute_write(
            agregar_ciudad,
            data.ciudad1,
            data.ciudad2,
            data.nueva,
            data.distancia1,
            data.latitud,
            data.longitud
        )
    return {"message": f"{data.nueva} agregada entre {data.ciudad1} y {data.ciudad2}"}

@app.post("/graph/delete-city")
def eliminar_intermedia(data: DeleteRequest):
    with driver.session() as session:
        session.execute_write(
            eliminar_ciudad,
            data.intermedia,
            data.ciudad1,
            data.ciudad2
        )
    return {"message": f"{data.intermedia} eliminada entre {data.ciudad1} y {data.ciudad2}, conectados directamente"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)