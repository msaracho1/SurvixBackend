from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth, catalog, guides, posts, routes, users

app = FastAPI(title="Survix API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://survixapp.com",
        "https://www.survixapp.com",
        "http://localhost:8081",
        "http://localhost:19006",
        "http://localhost:3000",
    ],
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


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
