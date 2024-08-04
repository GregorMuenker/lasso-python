"""app.py - This file contains the main application."""

import uvicorn
from fastapi import FastAPI
from middleware import BasicAuthMiddleware
from routes import init_routes

app = FastAPI()

app = init_routes(app)

app.add_middleware(BasicAuthMiddleware)

if __name__ == "__main__":
    uvicorn.run(app)
