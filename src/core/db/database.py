from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.db.models import Base
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession

from dotenv import load_dotenv
import os

load_dotenv()
user = os.getenv("DB_USER")
passwd = os.getenv("DB_PASSWD")
host = os.getenv("DB_HOST") #"db" #"localhost"
port = os.getenv("DB_PORT")
db = os.getenv("DB_NAME")

DB_URL = f'mysql+pymysql://{user}:{passwd}@{host}:{port}/{db}?charset=utf8'

engine = create_engine(
    DB_URL,
    echo=False,
    pool_size=10,
    max_overflow=20,
    pool_timeout=30
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()