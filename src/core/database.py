from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from core.models import Base

from dotenv import load_dotenv
import os

load_dotenv()
user = os.getenv("DB_USER")     # "root"
passwd = os.getenv("DB_PASSWD") # "1234"
host = os.getenv("DB_HOST")     # "127.0.0.1"
port = os.getenv("DB_PORT")     # "3306"
db = os.getenv("DB_NAME")       # "winectionDB"

DB_URL = f'mysql+pymysql://{user}:{passwd}@{host}:{port}/{db}?charset=utf8'

engine = create_engine(DB_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 테이블 생성
Base.metadata.create_all(bind=engine)

# FastAPI Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()