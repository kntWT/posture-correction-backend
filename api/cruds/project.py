from sqlalchemy.orm import Session
from models.project import Project as Model
from schemas.project import ProjectCreate, Project, ProjectGetByOwnerUserToken, ProjectGetByAppId
import secrets

def create_project(db: Session, project: ProjectCreate) -> Model:
    app_id = secrets.token_hex(16)  # 32文字のランダムな16進文字列
    p = Model(**project.model_dump(), app_id=app_id)
    db.add(p)
    db.commit()
    db.refresh(p)
    return p

def get_project_by_owner_user_token(db: Session, owner_user_token: str) -> list[Model]:
    return db.query(Model).filter(Model.owner_user_token == owner_user_token).all()

def get_project_by_app_id(db: Session, app_id: str) -> Model | None:
    return db.query(Model).filter(Model.app_id == app_id).one_or_none() 