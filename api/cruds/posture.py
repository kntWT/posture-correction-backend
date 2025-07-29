from sqlalchemy.orm import Session
from sqlalchemy import func, case
from models.posture import Posture as Model
from models.user import User
from schemas.posture import Posture, PostureOnlyFace, PostureOnlyPosition, PostureOnlySensor, PostureOnlyFilename, PostureCreate, PostureStats, PostureRankingItem
from cruds.user import get_user_by_token
from schemas.user import UserGetByToken
from datetime import datetime
import numpy as np


def get_postures(db: Session) -> list[Posture]:
    return db.query(Model).all()


def get_posture_by_id(db: Session, posture_id: int) -> list[Posture] | None:
    return db.query(Model).filter(Model.id == posture_id).one_or_none()


def get_posture_by_user_id(db: Session, user_id: int) -> list[Posture] | None:
    return db.query(Model).filter(Model.user_id == user_id).all()

def get_standard_posture_by_user_token(db: Session, token: str) -> Posture | None:
    user = get_user_by_token(db, UserGetByToken(token=token))
    return db.query(Model).filter(Model.id == user.standard_posture_id).one_or_none()


def create_posture(db: Session, posture: PostureCreate) -> Posture:
    p = Model(**posture.model_dump())
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


def update_filename(db: Session, posture: PostureOnlyFilename) -> Posture:
    p = db.query(Model).filter(Model.id == posture.id).first()
    p.file_name = posture.file_name
    db.commit()
    db.refresh(p)
    return p


def update_sensor(db: Session, posture: PostureOnlySensor) -> Posture:
    p = db.query(Model).filter(Model.id == posture.id).first()
    p.sensor_alpha = posture.sensor_alpha
    p.sensor_beta = posture.sensor_beta
    p.sensor_gamma = posture.sensor_gamma
    db.commit()
    db.refresh(p)
    return p


def update_face(db: Session, posture: PostureOnlyFace) -> Posture:
    p = db.query(Model).filter(Model.id == posture.id).first()
    p.face_pitch = posture.face_pitch
    p.face_yaw = posture.face_yaw
    p.face_roll = posture.face_roll
    db.commit()
    db.refresh(p)
    return p


def update_position(db: Session, posture: PostureOnlyPosition) -> Posture:
    p = db.query(Model).filter(Model.id == posture.id).first()
    p.nose_x = posture.nose_x
    p.nose_y = posture.nose_y
    p.neck_x = posture.neck_x
    p.neck_y = posture.neck_y
    p.neck_to_nose = posture.neck_to_nose
    p.standard_dist = posture.standard_dist
    db.commit()
    db.refresh(p)
    return p

def get_postures_by_app_id_and_user_id(db: Session, app_id: str, user_id: int, start_time: datetime = None, end_time: datetime = None) -> list[Model]:
    query =  db.query(Model).filter(Model.app_id == app_id, Model.user_id == user_id)
    if start_time:
        query = query.filter(Model.created_at >= start_time)
    if end_time:
        query = query.filter(Model.created_at <= end_time)
    return query.all()


def get_posture_stats(db: Session, app_id: str, user_id: int, threshold: int, start_time: datetime = None, end_time: datetime = None) -> PostureStats:
    query = db.query(Model).filter(
        Model.app_id == app_id,
        Model.user_id == user_id,
        Model.neck_angle.isnot(None)
    )
    if start_time:
        query = query.filter(
            Model.created_at >= start_time
        )
    if end_time:
        query = query.filter(
            Model.created_at <= end_time
        )
    
    postures = query.all()
    
    count = len(postures)
    if count == 0:
        return PostureStats(count=0, neck_angle_avg=None, neck_angle_std=None, good_posture_rate=None)
    
    neck_angles = [p.neck_angle for p in postures]
    
    neck_angle_avg = np.mean(neck_angles)
    neck_angle_std = np.std(neck_angles)
    
    good_posture_count = sum(1 for angle in neck_angles if angle <= threshold)
    good_posture_rate = good_posture_count / count if count > 0 else 0
    
    return PostureStats(
        count=count,
        neck_angle_avg=neck_angle_avg,
        neck_angle_std=neck_angle_std,
        good_posture_rate=good_posture_rate
    )


def get_posture_ranking(db: Session, app_id: str, threshold: int, limit: int = None, start_time: datetime = None, end_time: datetime = None) -> list[PostureRankingItem]:
    good_posture_count_case = func.sum(case([(Model.neck_angle <= threshold, 1)], else_=0))
    
    query = db.query(
        User.name,
        func.count(Model.id).label('count'),
        func.avg(Model.neck_angle).label('neck_angle_avg'),
        func.stddev(Model.neck_angle).label('neck_angle_std'),
        good_posture_count_case.label('good_posture_count')
    ).join(User, User.id == Model.user_id).filter(
        Model.app_id == app_id,
        Model.neck_angle.isnot(None)
    )

    if start_time:
        query = query.filter(Model.created_at >= start_time)
    if end_time:
        query = query.filter(Model.created_at <= end_time)

    query = query.group_by(User.name).order_by(func.avg(Model.neck_angle).asc())

    if limit:
        query = query.limit(limit)
    
    results = query.all()
    
    ranking = [
        PostureRankingItem(
            rank=i + 1,
            user_name=row.name,
            count=row.count,
            neck_angle_avg=row.neck_angle_avg,
            neck_angle_std=row.neck_angle_std,
            good_posture_rate=row.good_posture_count / row.count if row.count > 0 else 0
        ) for i, row in enumerate(results)
    ]
        
    return ranking
