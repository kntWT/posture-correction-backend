from sqlalchemy import Column, Integer, Boolean, String, Double, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from configs.db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    password = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    is_admin = Column(Boolean, default=False)
    standard_posture_id = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True))
    updated_at = Column(
        DateTime(timezone=True))

    postures = relationship("Posture", back_populates="owner")
