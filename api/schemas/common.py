from pydantic import BaseModel
from datetime import datetime
from helpers.jst import JST

class ResponseEx(BaseModel):
    status: bool
    message: str
    timestamp: datetime

    def __init__(self, msg: str):
        super().__init__(
            status=True,
            message=msg,
            timestamp=datetime.now(JST)
        )
