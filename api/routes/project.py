from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from schemas.user import User
from schemas.project import ProjectCreate, Project, ProjectGetByOwnerUserToken, ProjectGetByAppId
from schemas.http_exception import BadRequestException, NotFoundException, error_responses
from configs.db import get_db
import cruds.project as crud
from guards.app_id import require_app_id
from guards.auth import login_auth

project = APIRouter(prefix="/project", tags=["project"])

@project.get("/", response_model=Project, responses=error_responses([BadRequestException, NotFoundException]))
def get_project_by_app_id(app_id: str = Depends(require_app_id), db: Session = Depends(get_db)):
    p = crud.get_project_by_app_id(db, app_id)
    if p is None:
        raise NotFoundException("Project not found")
    return p

@project.get("/list", response_model=list[Project])
def get_project_by_owner_user_token(user: User = Depends(login_auth), db: Session = Depends(get_db)):
    owner_user_token = user.token
    return crud.get_project_by_owner_user_token(db, owner_user_token)

@project.post("/create", response_model=Project)
def create_project(project_create: ProjectCreate, db: Session = Depends(get_db)):
    return crud.create_project(db, project_create) 