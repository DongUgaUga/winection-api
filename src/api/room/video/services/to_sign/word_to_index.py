from sqlalchemy.orm import Session
from typing import Optional
from core.db.models import SignWord

def word_to_index(word: str, db: Session) -> Optional[int]:
    """
    단어에 해당하는 인덱스를 DB에서 조회
    """
    row = db.query(SignWord).filter(SignWord.word == word).first()
    return row.index if row else None

def get_all_sign_words(db: Session) -> list[str]:
    """
    수어 단어 DB에 저장된 단어들을 모두 반환
    """
    words = db.query(SignWord.word).all()
    return [w[0] for w in words]