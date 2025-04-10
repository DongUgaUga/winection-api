from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI

def add_cors_middleware(app: FastAPI):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "https://winection.kro.kr",
            "https://api.winection.kro.kr",
            "https://localhost:3000",
            "https://localhost:9090",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
