from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.routers import auth, catalog, guides, posts, routes, users, upload

app = FastAPI(title="Survix API", version="1.0.0")

_raw_origins = os.getenv(
    "ALLOWED_ORIGINS",
    "https://survixapp.com,https://www.survixapp.com,http://localhost:8081,http://localhost:19006,http://localhost:3000",
)
_origins = [o.strip() for o in _raw_origins.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(catalog.router)
app.include_router(users.router)
app.include_router(routes.router)
app.include_router(guides.router)
app.include_router(posts.router)
app.include_router(upload.router)

# Serve uploaded files as static assets at /files/<filename>
os.makedirs("uploads", exist_ok=True)
app.mount("/files", StaticFiles(directory="uploads"), name="files")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
