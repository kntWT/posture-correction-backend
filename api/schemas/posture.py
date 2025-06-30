from pydantic import Field, validator, AliasChoices
from datetime import datetime
from schemas.common import CamelCaseModel


class Posture(CamelCaseModel):
    id: int
    user_id: int
    file_name: str | None
    neck_angle: float | None
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
    standard_distance: float | None
    created_at: datetime | str | None
    updated_at: datetime | str
    app_id: str

    @validator("created_at", "updated_at", pre=True)
    def format_timestamp(cls, v: datetime) -> str:
        return v.strftime("%Y-%m-%d_%H:%M:%S.%f")


class PostureCreate(CamelCaseModel):
    user_id: int
    file_name: str | None
    neck_angle: float | None
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
    standard_distance: float | None
    created_at: datetime | str
    app_id: str


class PostureOnlySensor(CamelCaseModel):
    sensor_alpha: float | None = Field(validation_alias=AliasChoices(
        "alpha", "orientation_alpha", "orientationAlpha"))
    sensor_beta: float | None = Field(validation_alias=AliasChoices(
        "beta", "orientation_beta", "orientationBeta"))
    sensor_gamma: float | None = Field(validation_alias=AliasChoices(
        "gamma", "orientation_gamma", "orientationGamma"))


class PostureOnlyFace(CamelCaseModel):
    face_pitch: float | None = Field(alias="pitch")
    face_yaw: float | None = Field(alias="yaw")
    face_roll: float | None = Field(alias="roll")


class PostureOnlyPosition(CamelCaseModel):
    nose_x: float | None = Field(alias="noseX")
    nose_y: float | None = Field(alias="noseY")
    neck_x: float | None = Field(alias="neckX")
    neck_y: float | None = Field(alias="neckY")
    neck_to_nose: float | None = Field(alias="neckToNose")
    standard_distance: float | None = Field(alias="standardDist")


class PostureOnlyFilename(CamelCaseModel):
    id: int | None
    file_name: str
