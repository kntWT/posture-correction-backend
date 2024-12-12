from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from schemas.posture import Posture, PostureCreate, PostureOnlysensor, PostureOnlyFace, PostureOnlyPosition, PostureOnlyFilename
from schemas.user import User
import cruds.posture as crud
from guards.auth import login_auth, admin_auth
from configs.db import get_db

posture = APIRouter(prefix="/posture", tags=["posture"])


@posture.get("/", response_model=list[Posture])
async def get_postures(db: Session = Depends(get_db), _admin: User = Depends(admin_auth)):
    return crud.get_postures(db)


@posture.get("/{posture_id}", response_model=Posture)
async def get_posture_by_id(posture_id: int, db: Session = Depends(get_db), _login: User = Depends(login_auth)):
    return crud.get_posture_by_id(db, posture_id)


@posture.get("/user/{user_id}", response_model=list[Posture])
async def get_posture_by_user_id(user_id: int, db: Session = Depends(get_db), _login: User = Depends(login_auth)):
    return crud.get_posture_by_user_id(db, user_id)


@posture.post("/create", response_model=Posture)
async def create_posture(posture: PostureCreate, db: Session = Depends(get_db), _login: User = Depends(login_auth)):
    return crud.create_posture(db, posture)


@posture.put("/filename", response_model=Posture)
async def update_filename(posture: PostureOnlyFilename, db: Session = Depends(get_db)):
    return crud.update_filename(db, posture)


@posture.put("/sensor", response_model=Posture)
async def update_sensor(posture: PostureOnlysensor, db: Session = Depends(get_db)):
    return crud.update_sensor(db, posture)


@posture.put("/face", response_model=Posture)
async def update_face(posture: PostureOnlyFace, db: Session = Depends(get_db)):
    return crud.update_face(db, posture)


@posture.put("/position", response_model=Posture)
async def update_position(posture: PostureOnlyPosition, db: Session = Depends(get_db), _admin: User = Depends(admin_auth)):
    return crud.update_position(db, posture)
