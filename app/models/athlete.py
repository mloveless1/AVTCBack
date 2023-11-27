from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Athlete(Base):
    __tablename__ = "athletes"

    athlete_id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(255), index=True)
    date_of_birth = Column(Date)
    gender = Column(String(255))
    returner_status = Column(String(255))
    parent_id = Column(Integer, ForeignKey('parents.parent_id'))

    # Relationship to Parent model
    parent = relationship("Parent", back_populates="athletes")

    def to_dict(self):
        return {
            'athlete_id': self.athlete_id,
            'full_name': self.full_name,
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'gender': self.gender,
            'returner_status': self.returner_status,
            'parent_id': self.parent_id,
        }
