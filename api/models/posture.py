from sqlalchemy import Column, ForeignKey, Integer, String, Double, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql.functions import now
from configs.db import Base


class Posture(Base):
    __tablename__ = "postures"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    file_name = Column(String, default="")
    sensor_alpha = Column(Double)
    sensor_beta = Column(Double)
    sensor_gamma = Column(Double)
    face_pitch = Column(Double, nullable=True)
    face_roll = Column(Double, nullable=True)
    face_yaw = Column(Double, nullable=True)
    nose_x = Column(Double, nullable=True)
    nose_y = Column(Double, nullable=True)
    neck_x = Column(Double, nullable=True)
    neck_y = Column(Double, nullable=True)
    neck_to_nose = Column(Double, nullable=True)
    standard_distance = Column(Double, nullable=True)
    neck_angle = Column(Double, nullable=True)
    app_id = Column(String, index=True, nullable=False)
    created_at = Column(DateTime(timezone=True))
    updated_at = Column(
        DateTime(timezone=True), server_default=now(), onupdate=now())

    owner = relationship("User", back_populates="postures")

    class Config:
        orm_mode = True
