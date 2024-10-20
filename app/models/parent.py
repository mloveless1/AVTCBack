from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database import db
from .athlete import Athlete


class Parent(db.Model):
    __tablename__ = "parents"

    parent_id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(255))
    last_name = Column(String(255))
    suffix = Column(String(55))
    email = Column(String(255), unique=True, index=True)
    phone_number = Column(String(255))

    # Relationship to Athlete model
    athletes = relationship("Athlete", order_by=Athlete.athlete_id, back_populates="parent")
    address = relationship("Address", uselist=False, back_populates="parent")

    def to_dict(self):
        return {
            "parent_id": self.parent_id,
            'full_name': " ".join([self.first_name, self.last_name]),
            "email": self.email,
            "phone_number": self.phone_number,
        }
