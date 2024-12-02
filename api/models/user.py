from sqlalchemy import Column, Integer, String, Double, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql.func import now
from configs.db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    password = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    neck_to_nose_standard = Column(Double, nullable=True)
    created_at = Column(DateTime(TimeZone=True, server_default=now()))
    updated_at = Column(
        DateTime(TimeZone=True, server_default=now(), onupdate=now()))

    postures = relationship("Posture", back_populates="owner")
