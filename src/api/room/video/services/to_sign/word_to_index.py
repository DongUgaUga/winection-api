from sqlalchemy.orm import Session
from typing import Optional
from core.db.models import SignWord

def word_to_index(word: str, db: Session) -> Optional[int]:
    row = db.query(SignWord).filter(SignWord.word == word).first()
    return row.index if row else None

def get_all_sign_words(db: Session) -> list[str]:
    words = db.query(SignWord.word).all()
    return [w[0] for w in words]