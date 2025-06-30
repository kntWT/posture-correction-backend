from datetime import datetime
from schemas.common import CamelCaseModel

class ProjectCreate(CamelCaseModel):
    owner_user_token: str
    name: str

class Project(CamelCaseModel):
    id: int
    app_id: str
    name: str
    owner_user_token: str
    created_at: datetime
    updated_at: datetime 

class ProjectGetByOwnerUserToken(CamelCaseModel):
    owner_user_token: str

class ProjectGetByAppId(CamelCaseModel):
    app_id: str
