from fastapi import Header, HTTPException, status, Depends
from schemas.http_exception import BadRequestException, NotFoundException
from sqlalchemy.orm import Session
from configs.db import get_db
import cruds.project as crud

def require_app_id(app_id: str = Header(None), db: Session = Depends(get_db)) -> str:
    if not app_id or not isinstance(app_id, str) or app_id.strip() == "":
        raise BadRequestException("app_id header is required and must be a non-empty string.")
    project = crud.get_project_by_app_id(db, app_id)
    if project is None:
        raise NotFoundException("Project not found for given app_id.")
    return app_id 
