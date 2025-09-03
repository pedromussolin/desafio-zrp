from datetime import datetime, timezone
from . import db

class FidcCash(db.Model):
    __tablename__ = "fidc_cash"
    fidc_id = db.Column(db.String(40), primary_key=True)
    available_cash = db.Column(db.Float, nullable=False, default=1_000_000.0)
    updated_at = db.Column(db.DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
