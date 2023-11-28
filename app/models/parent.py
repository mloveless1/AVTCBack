from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base
from .athlete import Athlete


class Parent(Base):
    __tablename__ = "parents"

    parent_id = Column(Integer, primary_key=True, index=True)
    parent_name = Column(String(255), unique=True, index=True)
    email = Column(String(255), unique=True, index=True)
    phone_number = Column(String(255))

    # Relationship to Athlete model
    athletes = relationship("Athlete", order_by=Athlete.athlete_id, back_populates="parent")

    def to_dict(self):
        return {
            "parent_id": self.parent_id,
            "parent_name": self.parent_name,
            "email": self.email,
            "phone_number": self.phone_number,
        }