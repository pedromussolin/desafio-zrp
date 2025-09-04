from datetime import datetime, timezone
from app.models import db

class Operation(db.Model):
    __tablename__ = "operations"

    id = db.Column(db.String(50), primary_key=True)
    fidc_id = db.Column(db.String(40), db.ForeignKey("fidc_cash.fidc_id"), nullable=False)
    job_id = db.Column(db.String(36), db.ForeignKey("processing_jobs.job_id"), nullable=False)

    asset_code = db.Column(db.String(20), nullable=False)
    operation_type = db.Column(db.String(4), nullable=False)  # BUY|SELL
    quantity = db.Column(db.Integer, nullable=False)
    operation_date = db.Column(db.Date, nullable=False)

    status = db.Column(db.String(20), default="PENDING")  # PENDING|PROCESSING|COMPLETED|FAILED
    execution_price = db.Column(db.Float, nullable=True)
    total_value = db.Column(db.Float, nullable=True)
    tax_paid = db.Column(db.Float, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
