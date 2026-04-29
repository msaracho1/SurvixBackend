from fastapi import FastAPI

from app.routers import auth, catalog, guides, routes, users

app = FastAPI(title="Survix API", version="1.0.0")

app.include_router(auth.router)
app.include_router(catalog.router)
app.include_router(users.router)
app.include_router(routes.router)
app.include_router(guides.router)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
