from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from geolocation import router as geolocation_router

from functools import lru_cache

# ---------------- Settings ----------------


# ---------------- FastAPI app ----------------
app = FastAPI()



# ---------------- CORS ----------------
origins = [
    "http://localhost:3000",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------- Include routers ----------------

app.include_router(geolocation_router)