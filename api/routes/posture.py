from fastapi import APIRouter, Depends, File, UploadFile, Form, Body, Query
from pydantic_core import ValidationError
from sqlalchemy.orm import Session
from schemas.posture import Posture, PostureCreate, PostureOnlySensor, PostureOnlyFace, PostureOnlyPosition, PostureOnlyFilename, PostureStats, PostureRankingItem
from schemas.user import User
from schemas.http_exception import BadRequestException, UnauthorizedException, ForbiddenException, NotFoundException, error_responses
import cv2
import json
from datetime import datetime

import cruds.posture as crud
from configs.db import get_db
from configs.env import image_dir, timestamp_format, guest_id
from configs.estimator import guest_neck_to_nose_standard
from estimators.features.estimate import estimate_from_image as estimate_feature_from_image
from estimators.estimate import estimate_from_image, estimate_from_features
from guards.auth import login_auth, admin_auth
from guards.app_id import require_app_id
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


@posture.get("/user", response_model=list[Posture], responses=error_responses([UnauthorizedException]))
async def get_posture_by_user_id(user_id: int, db: Session = Depends(get_db), _login: User = Depends(login_auth)):
    return crud.get_posture_by_user_id(db, user_id)

@posture.get("/user/admin", response_model=list[Posture], responses=error_responses([UnauthorizedException]))
async def get_posture_by_user_id(user_id: int, db: Session = Depends(get_db), _admin: User = Depends(admin_auth)):
    return crud.get_posture_by_user_id(db, user_id)


@posture.post("/create", response_model=Posture, responses=error_responses([UnauthorizedException, BadRequestException, NotFoundException]))
async def create_posture(posture: PostureCreate, db: Session = Depends(get_db), _login: User = Depends(login_auth), app_id: str = Depends(require_app_id)):
    return crud.create_posture(db, PostureCreate(**posture, app_id=app_id))


@posture.post("/estimate", response_model=Posture, responses=error_responses([UnauthorizedException, BadRequestException, NotFoundException]))
async def estimate_posture(file: UploadFile = File(...), sensors: str = Form(...), enforce_calibration: bool = True, app_id: str = Depends(require_app_id), db: Session = Depends(get_db), user: User = Depends(login_auth)):
    try:
        sensors_json = json.loads(sensors)
        orientations = PostureOnlySensor(**sensors_json).model_dump()
    except json.JSONDecodeError:
        raise BadRequestException("Invalid JSON format")
    except ValidationError:
        raise BadRequestException("センサの値が無効です")
    
    standard_posture = crud.get_standard_posture_by_user_token(db, user.token)
    if enforce_calibration and standard_posture is None:
        raise BadRequestException("事前にキャリブレーションが必要です")

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
    
    neck_to_nose_standard = (standard_posture.neck_to_nose / standard_posture.standard_distance) if enforce_calibration else guest_neck_to_nose_standard
    height, width, _channel = img.shape
    neck_angle = await estimate_from_features({
        **face_feature, **head_feature, **orientations,
        "neck_to_nose_standard": neck_to_nose_standard,
        "image_width": width,
        "image_height": height,
    })
    return crud.create_posture(db, PostureCreate(
        **face_feature, **head_feature, **orientations,
        user_id=user.id, app_id=app_id, file_name=file.filename, image_width=width, image_height=height, neck_angle=neck_angle, created_at=timestamp))


@posture.post("/estimate/guest", response_model=Posture, responses=error_responses([BadRequestException, NotFoundException]))
async def estimate_posture(file: UploadFile = File(...), sensors: str = Form(...), app_id: str = Depends(require_app_id), db: Session = Depends(get_db)):
    try:
        sensors_json = json.loads(sensors)
        orientations = PostureOnlySensor(**sensors_json).model_dump()
    except json.JSONDecodeError:
        raise BadRequestException("Invalid JSON format")
    except ValidationError:
        raise BadRequestException("センサの値が無効です")

    # print(f"request recieved: {datetime.now()}")
    file_path = save_file(file.file, image_dir,
                          f"{guest_id}/original", file.filename)
    timestamp_str = file.filename.split(".jpg")[0]
    timestamp = datetime.strptime(f"{timestamp_str}000", timestamp_format)
    if file_path is None:
        raise BadRequestException("Failed to upload file")
    img = cv2.imread(file_path)
    face_feature, head_feature = await estimate_feature_from_image(img, guest_id, file.filename)
    if face_feature is None:
        raise BadRequestException("顔が認識できませんでした。\n顔が隠れないようにし、画面から離れて首元が映るようにしてください。")
    if head_feature is None:
        raise BadRequestException("顔が認識できませんでした。\n顔が隠れないようにしてください。")
    
    # print(f"neck angle estimate start: {datetime.now()}")
    height, width, _channel = img.shape
    neck_angle = await estimate_from_features({
        **face_feature,
        **head_feature,
        **orientations,
        "neck_to_nose_standard": guest_neck_to_nose_standard,
        "image_width": width,
        "image_height": height,
    })
    # print(f"neck angle estimate finish: {datetime.now()}")
    return crud.create_posture(db, PostureCreate(
        **face_feature, **head_feature, **orientations,
        user_id=guest_id, app_id=app_id, file_name=file.filename, image_width=width, image_height=height, neck_angle=neck_angle, created_at=timestamp))


@posture.post("/estimate/feature", response_model=Posture, responses=error_responses([UnauthorizedException, BadRequestException, NotFoundException]))
async def estimate_feature(file: UploadFile = File(...), sensors: str = Form(...), app_id: str = Depends(require_app_id), db: Session = Depends(get_db), user: User = Depends(login_auth)):
    try:
        sensors_json = json.loads(sensors)
        orientations = PostureOnlySensor(**sensors_json).model_dump()
    except json.JSONDecodeError:
       raise BadRequestException("Invalid JSON format")
    except ValidationError:
        raise BadRequestException("センサの値が無効です")
    
    file_path = save_file(file.file, image_dir,
                          f"{user.id}/original", file.filename)
    if file_path is None:
        raise BadRequestException("Failed to upload file")
    img = cv2.imread(file_path)
    face_feature, head_feature = await estimate_feature_from_image(img, user.id, file.filename)
    if face_feature is None:
        raise BadRequestException("顔が認識できませんでした。\n顔が隠れないようにし、画面から離れて首元が映るようにしてください。")
    if head_feature is None:
        raise BadRequestException("顔が認識できませんでした。\n顔が隠れないようにしてください。")
    timestamp_str = file.filename.split(".jpg")[0]
    timestamp = datetime.strptime(f"{timestamp_str}000", timestamp_format)
    height, width, _channel = img.shape
    return crud.create_posture(db, PostureCreate(
        **face_feature, **head_feature, **orientations,
        user_id=user.id, app_id=app_id, file_name=file.filename, image_width=width, image_height=height, created_at=timestamp, neck_angle=None))


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


@posture.get("/app", response_model=list[Posture], responses=error_responses([UnauthorizedException, BadRequestException, NotFoundException]))
async def get_my_postures_by_app_id(start_time: datetime, end_time: datetime = None, db: Session = Depends(get_db), user: User = Depends(login_auth), app_id: str = Depends(require_app_id)):
    return crud.get_postures_by_app_id_and_user_id(db, app_id, user.id, start_time, end_time)


@posture.get("/app/admin/{user_id}", response_model=list[Posture], responses=error_responses([UnauthorizedException, ForbiddenException, BadRequestException, NotFoundException]))
async def get_user_postures_by_app_id(user_id: int, db: Session = Depends(get_db), _admin: User = Depends(admin_auth), app_id: str = Depends(require_app_id)):
    return crud.get_postures_by_app_id_and_user_id(db, app_id, user_id)


@posture.get("/app/stats/admin/{user_id}", response_model=PostureStats, responses=error_responses([UnauthorizedException, ForbiddenException, BadRequestException, NotFoundException]))
async def get_user_posture_stats_by_app_id(user_id: int, threshold: int = Query(30, ge=0, le=90), db: Session = Depends(get_db), _admin: User = Depends(admin_auth), app_id: str = Depends(require_app_id)):
    return crud.get_posture_stats(db, app_id, user_id, threshold)


@posture.get("/app/stats", response_model=PostureStats, responses=error_responses([UnauthorizedException, BadRequestException, NotFoundException]))
async def get_my_posture_stats_by_app_id(start_time: datetime = None, end_time: datetime = None, threshold: int = Query(30, ge=0, le=90), db: Session = Depends(get_db), user: User = Depends(login_auth), app_id: str = Depends(require_app_id)):
    return crud.get_posture_stats(db, app_id, user.id, threshold, start_time, end_time)


@posture.get("/app/ranking", response_model=list[PostureRankingItem], responses=error_responses([UnauthorizedException, BadRequestException, NotFoundException]))
async def get_posture_ranking(
    limit: int = Query(None, ge=1), 
    threshold: int = Query(30, ge=0, le=90), 
    start_time: datetime = None,
    end_time: datetime = None,
    db: Session = Depends(get_db), 
    _user: User = Depends(login_auth), 
    app_id: str = Depends(require_app_id)
):
    return crud.get_posture_ranking(db, app_id, threshold, limit, start_time, end_time)
