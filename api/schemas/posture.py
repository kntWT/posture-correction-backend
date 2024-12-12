from pydantic import BaseModel, Field, validator
from datetime import datetime


class Posture(BaseModel):
    id: int
    user_id: int
    file_name: str | None
    sensor_alpha: float | None
    sensor_beta: float | None
    sensor_gamma: float | None
    face_pitch: float | None
    face_yaw: float | None
    face_roll: float | None
    nose_x: float | None
    nose_y: float | None
    neck_x: float | None
    neck_y: float | None
    neck_to_nose: float | None
    standard_dist: float | None
    created_at: datetime | str | None
    updated_at: datetime | str

    @validator("created_at", "updated_at", pre=True)
    def format_timestamp(cls, v: datetime) -> str:
        return v.strftime("%Y-%m-%d_%H:%M:%S.%f")


class PostureCreate(BaseModel):
    user_id: int
    file_name: str | None
    sensor_alpha: float | None
    sensor_beta: float | None
    sensor_gamma: float | None
    face_pitch: float | None
    face_yaw: float | None
    face_roll: float | None
    nose_x: float | None
    nose_y: float | None
    neck_x: float | None
    neck_y: float | None
    neck_to_nose: float | None
    standard_dist: float | None


class PostureOnlysensor(BaseModel):
    user_id: int = Field(alias="userId")
    sensor_alpha: float | None = Field(alias="alpha")
    sensor_beta: float | None = Field(alias="beta")
    sensor_gamma: float | None = Field(alias="gamma")


class PostureOnlyFace(BaseModel):
    face_pitch: float | None = Field(alias="pitch")
    face_yaw: float | None = Field(alias="yaw")
    face_roll: float | None = Field(alias="roll")


class PostureOnlyPosition(BaseModel):
    nose_x: float | None = Field(alias="noseX")
    nose_y: float | None = Field(alias="noseY")
    neck_x: float | None = Field(alias="neckX")
    neck_y: float | None = Field(alias="neckY")
    neck_to_nose: float | None = Field(alias="neckToNose")
    standard_dist: float | None = Field(alias="standardDist")


class PostureOnlyFilename(BaseModel):
    id: int | None
    file_name: str
