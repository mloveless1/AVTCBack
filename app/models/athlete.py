from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.database import db


class Athlete(db.Model):
    __tablename__ = "athletes"

    athlete_id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(255))
    last_name = Column(String(255))
    suffix = Column(String(50))
    date_of_birth = Column(Date)
    gender = Column(String(255))
    returner_status = Column(String(255))
    parent_id = Column(Integer, ForeignKey('parents.parent_id'))
    medical_conditions = Column(String(255))

    # Relationship to Parent model
    parent = relationship("Parent", back_populates="athletes")

    def to_dict(self):
        return {
            'athlete_id': self.athlete_id,
            'full_name': " ".join([self.first_name, self.last_name]),
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'gender': self.gender,
            'returner_status': self.returner_status,
            'parent_id': self.parent_id,
            'medical_conditions': self.medical_conditions,
        }
