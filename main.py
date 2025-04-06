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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)