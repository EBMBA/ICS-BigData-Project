from fastapi import FastAPI
import uvicorn
from Annotation import Annotation
import requests

app = FastAPI()

@app.get("/annotation")
async def annotate_pictures():
    print('annotation received')
    annotation = Annotation()
    annotation.run()
    url = 'http://recommandation:8080/analyse'

    response = requests.get(url)

if __name__=="__main__":
    uvicorn.run("main:app",host='0.0.0.0', port=3001, reload=True)
