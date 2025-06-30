from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel
from datetime import datetime
from helpers.jst import JST

class CamelCaseModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True
    )

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
