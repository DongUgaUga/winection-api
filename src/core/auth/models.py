from sqlalchemy import Integer, String, Boolean
from sqlalchemy.orm import mapped_column, declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    username = mapped_column(String(50), unique=True, nullable=False)     # 아이디
    password = mapped_column(String(255), nullable=False)                 # 비밀번호 (해시)
    nickname = mapped_column(String(50), nullable=False)                  # 닉네임
    user_type = mapped_column(String(20), nullable=False)                 # 농민 / 일반인 / 응급기관

    emergency_type = mapped_column(String(20), nullable=True)             # 병원 / 경찰서 / 소방서
    address = mapped_column(String(255), nullable=True)
    organization_name = mapped_column(String(100), nullable=True)

    is_active = mapped_column(Boolean, default=True)