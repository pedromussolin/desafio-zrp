from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime
from app import db

class Operation(db.Model):
    __tablename__ = 'operations'

    id = Column(Integer, primary_key=True)
    asset_code = Column(String(10), nullable=False)
    operation_type = Column(String(4), nullable=False)  # e.g., 'BUY' or 'SELL'
    quantity = Column(Float, nullable=False)
    status = Column(String(20), default='PENDING')  # e.g., 'PENDING', 'COMPLETED', 'FAILED'
    execution_price = Column(Float, nullable=False)
    total_value = Column(Float, nullable=False)
    tax_paid = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Operation {self.id}: {self.operation_type} {self.quantity} of {self.asset_code}>'