from app import db
from sqlalchemy.dialects.postgresql import UUID
import uuid

class Organisation(db.Model):
    orgId = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String)
    ownerId = db.Column(UUID(as_uuid=True), db.ForeignKey('user.userId'), nullable=False)

    def __repr__(self):
        return f"<Organisation {self.name}>"
