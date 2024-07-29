"""app.py - This file contains the main application."""

import uvicorn
from fastapi import FastAPI

from routes import init_routes

app = FastAPI()

app = init_routes(app)

if __name__ == "__main__":
    uvicorn.run(app, debug=True)
