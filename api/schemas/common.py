from pydantic import BaseModel
from datetime import datetime
from helpers.jst import JST

class ResponseEx(BaseModel):
    status: bool
    message: str
    timestamp: datetime

    def __init__(self, msg: str):
        self.status = True
        self.message = msg
        self.timestamp = datetime.now(JST)
