from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from configs.db import Base

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    app_id = Column(String(32), nullable=False)
    name = Column(Text, nullable=False)
    owner_user_token = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    class Config:
        orm_mode = True 