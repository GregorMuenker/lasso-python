"""app.py - This file contains REST API."""

import uvicorn
from fastapi import FastAPI
from crawl_pipeline import index_package

app = FastAPI()

@app.post("/crawl/{package_name}")
def crawl(package_name: str, type_inference: str = None):
    type_inference_param = type_inference == "True"
    return index_package(package_name, type_inference_param)

@app.get("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
