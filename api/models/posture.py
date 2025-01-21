from sqlalchemy import Column, ForeignKey, Integer, String, Double, DateTime
from sqlalchemy.orm import relationship
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
    created_at = Column(DateTime(timezone=True))
    updated_at = Column(
        DateTime(timezone=True))

    owner = relationship("User", back_populates="postures")
