from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes.prompts import router as prompts_router
from .db import init_db

app = FastAPI(title="Prompt Gauge — Core Generation MVP")

# Initialize database on startup
@app.on_event("startup")
def startup_event():
    init_db()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(prompts_router, prefix="")
