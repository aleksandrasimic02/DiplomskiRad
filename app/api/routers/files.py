from __future__ import annotations
import secrets, unicodedata
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from fastapi.responses import FileResponse
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND
from app.core.config import settings

router = APIRouter(prefix="/files", tags=["files"])

def _slugify(filename: str) -> str:
    s = unicodedata.normalize("NFKD", filename).encode("ascii", "ignore").decode("ascii")
    s = s.replace(" ", "_")
    return "".join(ch for ch in s if ch.isalnum() or ch in {".", "_", "-"})

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
):
    ext = Path(file.filename).suffix.lower()
    if ext not in settings.ALLOWED_UPLOAD_EXTS:
        raise HTTPException(HTTP_400_BAD_REQUEST, f"Nedozvoljen tip fajla: {ext}")

    # veličina (ako želiš da striktno meriš – čitaj u bufferu)
    # ovde bez teške validacije; oslanjamo se na reverse proxy/nginx limit

    # ime: {random}__{original_slug}
    rand = secrets.token_hex(16)
    safe_name = _slugify(file.filename) or f"file{ext}"
    stored_name = f"{rand}__{safe_name}"
    dest = settings.UPLOAD_DIR / stored_name

    # snimi na disk
    with dest.open("wb") as out:
        while True:
            chunk = await file.read(1024 * 1024)
            if not chunk:
                break
            out.write(chunk)

    # vrati identifikator i lep url do download-a
    return {
        "id": stored_name,               # ovo upisuj u DB polje (recept_dokument / dokument_starateljstva)
        "original_name": file.filename,  # možeš i ovo da čuvaš u dodatnom polju, ako želiš
        "url": f"/files/{stored_name}",  # GET download
    }

@router.get("/{file_id}")
def download_file(file_id: str, ):
    # (opciono) ovde možeš da dodaš autorizaciju po ulozi/entitetu
    path = settings.UPLOAD_DIR / file_id
    if not path.exists():
        raise HTTPException(HTTP_404_NOT_FOUND, "Fajl nije pronađen.")

    # izvuci originalno ime iz "{rand}__{original}"
    original = file_id.split("__", 1)[1] if "__" in file_id else path.name
    # forsiraj download
    return FileResponse(
        path,
        media_type="application/octet-stream",
        filename=original,
    )
