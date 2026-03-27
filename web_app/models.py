from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class TargetSequenceLog(db.Model):
    __tablename__ = 'sequence_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    audit_hash = db.Column(db.String(32), unique=True, nullable=False)
    sequence = db.Column(db.String(100), nullable=False)
    gc_content = db.Column(db.Float, nullable=False)
    efficacy = db.Column(db.Float, nullable=False)
    safety_score = db.Column(db.Float, nullable=False)
    risk_factors = db.Column(db.Text, nullable=True) # Comma separated list of risks
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            "id": self.id,
            "audit_hash": self.audit_hash,
            "sequence": self.sequence,
            "gc_content": self.gc_content,
            "efficacy": self.efficacy,
            "safety_score": self.safety_score,
            "risk_factors": self.risk_factors,
            "timestamp": self.timestamp.isoformat() + "Z"
        }
