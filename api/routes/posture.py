from fastapi import APIRouter, Depends, File, UploadFile, Form, Body
from sqlalchemy.orm import Session
from schemas.posture import Posture, PostureCreate, PostureOnlySensor, PostureOnlyFace, PostureOnlyPosition, PostureOnlyFilename
from schemas.user import User
from schemas.http_exception import BadRequestException, UnauthorizedException, ForbiddenException, NotFoundException, error_responses
import cv2
import json
from datetime import datetime

import cruds.posture as crud
from configs.db import get_db
from configs.env import image_dir, timestamp_format
from estimators.features.estimate import estimate_from_image as estimate_feature_from_image
from estimators.estimate import estimate_from_image, estimate_from_features
from guards.auth import login_auth, admin_auth
from helpers.save_file import save_file

posture = APIRouter(prefix="/posture", tags=["posture"])


@posture.get("/", response_model=list[Posture], responses=error_responses([UnauthorizedException, ForbiddenException]))
async def get_postures(db: Session = Depends(get_db), _admin: User = Depends(admin_auth)):
    return crud.get_postures(db)


@posture.get("/{posture_id}", response_model=Posture, responses=error_responses([NotFoundException, UnauthorizedException, ForbiddenException]))
async def get_posture_by_id(posture_id: int, db: Session = Depends(get_db), _login: User = Depends(login_auth)):
    p = crud.get_posture_by_id(db, posture_id)
    if p is None:
        raise NotFoundException("No posture found")


@posture.get("/user/{user_id}", response_model=list[Posture], responses=error_responses([UnauthorizedException]))
async def get_posture_by_user_id(user_id: int, db: Session = Depends(get_db), _login: User = Depends(login_auth)):
    return crud.get_posture_by_user_id(db, user_id)


@posture.post("/create", response_model=Posture, responses=error_responses([UnauthorizedException]))
async def create_posture(posture: PostureCreate, db: Session = Depends(get_db), _login: User = Depends(login_auth)):
    return crud.create_posture(db, posture)


@posture.post("/estimate", response_model=Posture, responses=error_responses([UnauthorizedException, BadRequestException]))
async def estimate_posture(file: UploadFile = File(...), sensors: str = Form(...), db: Session = Depends(get_db), user: User = Depends(login_auth)):
    try:
        sensors_json = json.loads(sensors)
        orientations = PostureOnlySensor(**sensors_json).model_dump()
    except json.JSONDecodeError:
        raise("Invalid JSON format")

    file_path = save_file(file.file, image_dir,
                          f"{user.id}/original", file.filename)
    timestamp_str = file.filename.split(".jpg")[0]
    timestamp = datetime.strptime(f"{timestamp_str}000", timestamp_format)
    if file_path is None:
        raise BadRequestException("Failed to upload file")
    img = cv2.imread(file_path)
    face_feature, head_feature = await estimate_feature_from_image(img, user.id, file.filename)
    if face_feature is None:
        raise BadRequestException("顔が認識できませんでした。\n顔が隠れないようにし、画面から離れて首元が映るようにしてください。")
    if head_feature is None:
        raise BadRequestException("顔が認識できませんでした。\n顔が隠れないようにしてください。")
    
    neck_angle = await estimate_from_features({**face_feature, **head_feature, **orientations})
    return crud.create_posture(db, PostureCreate(
        **face_feature, **head_feature, **orientations,
        user_id=user.id, file_name=file.filename, neck_angle=neck_angle, created_at=timestamp))


@posture.post("/estimate/feature", response_model=Posture, responses=error_responses([UnauthorizedException, BadRequestException]))
async def estimate_feature(file: UploadFile = File(...), sensors: str = Form(...), db: Session = Depends(get_db), user: User = Depends(login_auth)):
    try:
        sensors_json = json.loads(sensors)
        orientations = PostureOnlySensor(**sensors_json).model_dump()
    except json.JSONDecodeError:
       raise("Invalid JSON format")
    
    file_path = save_file(file.file, image_dir,
                          f"original/{user.id}", file.filename)
    if file_path is None:
        raise BadRequestException("Failed to upload file")
    img = cv2.imread(file_path)
    face_feature, head_feature = await estimate_feature_from_image(img, user.id, file.filename)
    if face_feature is None or head_feature is None:
        raise BadRequestException("Failed to estimate posture")
    timestamp_str = file.filename.split(".jpg")[0]
    timestamp = datetime.strptime(f"{timestamp_str}000", timestamp_format)
    return crud.create_posture(db, PostureCreate(
        **face_feature, **head_feature, **orientations,
        user_id=user.id, file_name=file.filename, created_at=timestamp))


@posture.put("/filename", response_model=Posture, responses=error_responses([UnauthorizedException, ForbiddenException]))
async def update_filename(posture: PostureOnlyFilename, db: Session = Depends(get_db), _admin: User = Depends(admin_auth)):
    return crud.update_filename(db, posture)


@posture.put("/sensor", response_model=Posture, responses=error_responses([UnauthorizedException, ForbiddenException]))
async def update_sensor(posture: PostureOnlySensor, db: Session = Depends(get_db), _admin: User = Depends(admin_auth)):
    return crud.update_sensor(db, posture)


@posture.put("/face", response_model=Posture, responses=error_responses([UnauthorizedException, ForbiddenException]))
async def update_face(posture: PostureOnlyFace, db: Session = Depends(get_db), _admin: User = Depends(admin_auth)):
    return crud.update_face(db, posture)


@posture.put("/position", response_model=Posture, responses=error_responses([UnauthorizedException, ForbiddenException]))
async def update_position(posture: PostureOnlyPosition, db: Session = Depends(get_db), _admin: User = Depends(admin_auth)):
    return crud.update_position(db, posture)
