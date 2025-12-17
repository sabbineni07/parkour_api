from app import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import ARRAY

class Dataset(db.Model):
    __tablename__ = 'datasets'
    
    dataset_id = db.Column(db.String(255), primary_key=True)
    dataset_name = db.Column(db.String(255), nullable=False)
    dataset_type = db.Column(db.String(100), nullable=False)
    layer = db.Column(db.String(100), nullable=False)
    upstream_dependencies = db.Column(ARRAY(db.String), nullable=True, default=list)
    status = db.Column(db.String(50), nullable=False, default='active')
    created_ts = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_ts = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def to_dict(self):
        """Convert dataset to dictionary"""
        return {
            'dataset_id': self.dataset_id,
            'dataset_name': self.dataset_name,
            'dataset_type': self.dataset_type,
            'layer': self.layer,
            'upstream_dependencies': self.upstream_dependencies or [],
            'status': self.status,
            'created_ts': self.created_ts.isoformat() if self.created_ts else None,
            'updated_ts': self.updated_ts.isoformat() if self.updated_ts else None
        }
    
    def __repr__(self):
        return f'<Dataset {self.dataset_id}: {self.dataset_name}>'

