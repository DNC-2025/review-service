from sqlalchemy import Column, BigInteger, Integer, Text, DateTime, func, CheckConstraint
from app.database.config import Base

class Review(Base):
    __tablename__ = "review"
    __table_args__ = (CheckConstraint('rating >= 1 AND rating <= 5', name='rating_range_check'),)

    # app/models/tables.py
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False, index=True)       
    content_id = Column(BigInteger, nullable=False, index=True)    
    rating = Column(Integer, nullable=False)
    review_text = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


    def __init__(self, user_id: int, content_id: int, rating: int, review_text: str = None):
        self.user_id = user_id
        self.content_id = content_id
        self.rating = rating
        self.review_text = review_text

    def __repr__(self):
        return f"Review(id={self.id}, user_id={self.user_id}, content_id={self.content_id}, rating={self.rating}, review_text={self.review_text})"

