from fastapi import FastAPI
import uvicorn
from Annotation import Annotation

app = FastAPI()

@app.get("/annotation")
async def annotate_pictures():
    annotation = Annotation()
    annotation.run()

if __name__=="__main__":
    uvicorn.run("main:app",host='0.0.0.0', port=3001, reload=True)