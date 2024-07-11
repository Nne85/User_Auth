from app import db
from sqlalchemy.dialects.postgresql import UUID
import uuid

user_organisation = db.Table('user_organisation',
    db.Column('userId', UUID(as_uuid=True), db.ForeignKey('user.userId'), primary_key=True),
    db.Column('orgId', UUID(as_uuid=True), db.ForeignKey('organisation.orgId'), primary_key=True)
)


class User(db.Model):

    userId = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,
                       unique=True, nullable=False)
    firstName = db.Column(db.String, nullable=False)
    lastName = db.Column(db.String, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    phone = db.Column(db.String)
    owned_organisations = db.relationship('Organisation', backref='owner', lazy=True)
    organisations = db.relationship('Organisation', secondary=user_organisation, lazy='subquery',
        backref=db.backref('users', lazy=True))


    def __repr__(self):
        return f"<User {self.userId}>"
