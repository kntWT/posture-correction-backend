from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import time

from configs.env import user, password, db_name, host


def connect_db(trial: int):
    if trial >= 30:
        print("connection refused")
        return None, None, None
    try:
        engine = create_engine(
            f'mysql+pymysql://{user}:{password}@{host}/{db_name}')
        SessionLocal = sessionmaker(bind=engine)
        Base = declarative_base()
        return engine, SessionLocal, Base
    except Exception as e:
        time.sleep(1)
        print(e)
        return connect_db(trial + 1)


engine, SessionLocal, Base = connect_db(0)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
