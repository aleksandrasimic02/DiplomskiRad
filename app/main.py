from fastapi import FastAPI
import os

from starlette.responses import FileResponse
from starlette.staticfiles import StaticFiles

from app.core.config import settings
from app.db.init_db import init_db
from app.api.routers import (
    korisnici, administratori, apoteke, obavestenja, staratelji, lekovi, pretplate, auth, profile, public, apoteka_portal, korisnik_portal, apoteka_manage, admin_portal, staratelj_portal, files
)

from app.core.config import settings
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title=settings.API_TITLE, version=settings.API_VERSION)

origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5500",  # VS Code Live Server, npr.
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],            # ili koristi allow_origin_regex dole
    allow_credentials=False,          # True samo ako koristiš cookies/sessions
    allow_methods=["*"],              # GET, POST, PUT, DELETE, OPTIONS...
    allow_headers=["*"],              # uključujući Authorization, Content-Type
    expose_headers=["*"],             # po potrebi
)
@app.on_event("startup")
def on_startup():
    init_db()

app.include_router(korisnici.router)
app.include_router(administratori.router)
app.include_router(apoteke.router)
app.include_router(staratelji.router)
app.include_router(lekovi.router)
app.include_router(pretplate.router)
app.include_router(auth.router)
app.include_router(profile.router)
app.include_router(public.router)
app.include_router(apoteka_portal.router)
app.include_router(korisnik_portal.router)
app.include_router(apoteka_manage.router)
app.include_router(admin_portal.router)
app.include_router(staratelj_portal.router)
app.include_router(files.router)
app.include_router(obavestenja.router)


STATIC_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend")
STATIC_DIR = os.path.abspath(STATIC_DIR)

if os.path.isdir(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

    @app.get("/")
    async def index():
        index_path = os.path.join(STATIC_DIR, "index.html")
        return FileResponse(index_path)