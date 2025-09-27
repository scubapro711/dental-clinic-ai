from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

def setup_middleware(app: FastAPI):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production, you should restrict this
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

