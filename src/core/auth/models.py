from sqlalchemy import String, Integer, Boolean, Float
from sqlalchemy.orm import mapped_column, declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    username = mapped_column(String(50), unique=True, nullable=False)
    password = mapped_column(String(255), nullable=False)
    nickname = mapped_column(String(50), nullable=False)
    phone_number = mapped_column(String(20), nullable=False)
    user_type = mapped_column(String(20), nullable=False)
    emergency_type = mapped_column(String(20), nullable=True)
    address = mapped_column(String(255), nullable=True)
    organization_name = mapped_column(String(100), nullable=True)
    latitude = mapped_column(Float, nullable=True)
    longitude = mapped_column(Float, nullable=True)
    is_active = mapped_column(Boolean, default=True)
    emergency_code = mapped_column(String(7), unique=True, nullable=True)