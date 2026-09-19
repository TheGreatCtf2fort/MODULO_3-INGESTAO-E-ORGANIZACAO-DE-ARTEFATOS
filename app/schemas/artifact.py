from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ArtifactResponse(BaseModel):
    id: int
    project_id: int
    name: str
    artifact_type: str
    file_path: str
    version: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)