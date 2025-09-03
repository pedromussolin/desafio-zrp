from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Price(Base):
    __tablename__ = 'prices'

    id = Column(Integer, primary_key=True)
    asset_code = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Price(asset_code='{self.asset_code}', price={self.price}, created_at='{self.created_at}')>"