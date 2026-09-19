from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Artifact, Project
from app.schemas.artifact import ArtifactResponse


router = APIRouter(
    prefix="/projects/{project_id}/artifacts",
    tags=["Artifacts"],
)


STORAGE_DIR = Path("storage")


ALLOWED_TYPES = {
    "application/pdf": "PDF",
    "text/markdown": "MARKDOWN",
    "image/png": "PNG",
    "image/jpeg": "JPEG",
}


@router.post(
    "/",
    response_model=ArtifactResponse,
)
async def upload_artifact(
    project_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    project = db.get(Project, project_id)

    if project is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found",
        )

    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type",
        )

    project_dir = STORAGE_DIR / str(project_id)
    project_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    file_path = project_dir / file.filename

    file_content = await file.read()

    file_path.write_bytes(file_content)

    artifact = Artifact(
        project_id=project_id,
        name=file.filename,
        artifact_type=ALLOWED_TYPES[file.content_type],
        file_path=str(file_path),
        version=1,
    )

    db.add(artifact)
    db.commit()
    db.refresh(artifact)

    return artifact