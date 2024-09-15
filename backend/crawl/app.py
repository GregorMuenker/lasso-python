"""app.py - This file contains REST API."""

import uvicorn
from fastapi import FastAPI, Request
from crawl_pipeline import index_package

app = FastAPI()

@app.post("/crawl/{package_name}")
def crawl(package_name: str, request: Request):
    return index_package(package_name, type_inferencing_engine=request.query_params.get('type_inferencing_engine', None))

@app.get("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
