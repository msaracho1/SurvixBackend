import os
import uuid

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile

from app.dependencies.auth import get_current_user
from app.models.entities import User

router = APIRouter(prefix="/upload", tags=["upload"])

UPLOAD_DIR = "uploads"
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp", "gif"}
MAX_SIZE_BYTES = 8 * 1024 * 1024  # 8 MB

# Magic bytes signatures for allowed image types
_MAGIC: list[tuple[bytes, str]] = [
    (b"\xff\xd8\xff", "jpg"),
    (b"\x89PNG\r\n\x1a\n", "png"),
    (b"GIF87a", "gif"),
    (b"GIF89a", "gif"),
    (b"RIFF", "webp"),  # followed by WEBP at offset 8, checked below
]

os.makedirs(UPLOAD_DIR, exist_ok=True)


def _validate_magic(contents: bytes) -> bool:
    for magic, _ in _MAGIC:
        if contents.startswith(magic):
            if magic == b"RIFF":
                return len(contents) >= 12 and contents[8:12] == b"WEBP"
            return True
    return False


@router.post("/image")
async def upload_image(
    request: Request,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
) -> dict:
    ext = (file.filename or "").rsplit(".", 1)[-1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Formato no permitido. Usá: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    contents = await file.read()
    if len(contents) > MAX_SIZE_BYTES:
        raise HTTPException(status_code=413, detail="La imagen supera el límite de 8 MB.")

    if not _validate_magic(contents):
        raise HTTPException(status_code=400, detail="El contenido del archivo no corresponde a una imagen válida.")

    filename = f"{uuid.uuid4()}.{ext}"
    path = os.path.join(UPLOAD_DIR, filename)
    with open(path, "wb") as f:
        f.write(contents)

    base_url = str(request.base_url).rstrip("/")
    return {"url": f"{base_url}/files/{filename}"}
