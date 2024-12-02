from sqlalchemy import create_engine, MetaData
import time

from config.env import user, password, db_name, host

def connect_db(trial: int):
    if trial >= 30:
        print("connection refused")
        return None, None, None
    try:
        engine = create_engine(f'mysql+pymysql://{user}:{password}@mysql:3306/{db_name}')
        meta = MetaData()
        conn = engine.connect()
        return engine, meta, conn
    except Exception as e:
        time.sleep(1)
        print(e)
        print(host)
        return connect_db(trial + 1)
    
engine, meta, conn = connect_db(0)