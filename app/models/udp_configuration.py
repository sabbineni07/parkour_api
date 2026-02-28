from app import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSONB


class UDPConfiguration(db.Model):
    """UDP (Unified Data Pipeline) configuration storage"""
    __tablename__ = 'udp_configurations'

    name = db.Column(db.String(255), primary_key=True)
    kind = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    options = db.Column(JSONB, nullable=True, default=list)  # [{key, value}]
    spec = db.Column(JSONB, nullable=False)  # {input, extract_query, transform, schema, output}
    spark_config = db.Column(JSONB, nullable=True, default=list)  # [{key, value}]
    created_ts = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_ts = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def to_dict(self):
        """Convert to dict matching frontend UDPConfiguration interface"""
        return {
            'name': self.name,
            'kind': self.kind,
            'author': self.author,
            'description': self.description or '',
            'options': self.options or [],
            'spec': self.spec or {},
            'spark_config': self.spark_config or []
        }

    def __repr__(self):
        return f'<UDPConfiguration {self.name}>'
