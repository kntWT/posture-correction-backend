from pydantic import BaseModel
from datetime import datetime

class ProjectCreate(BaseModel):
    owner_user_token: str
    name: str

class Project(BaseModel):
    id: int
    app_id: str
    name: str
    owner_user_token: str
    created_at: datetime
    updated_at: datetime 

class ProjectGetByOwnerUserToken(BaseModel):
    owner_user_token: str

class ProjectGetByAppId(BaseModel):
    app_id: str