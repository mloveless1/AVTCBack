from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import db


class Address(db.Model):
    __tablename__ = "addresses"

    address_id = Column(Integer, primary_key=True, index=True)
    street_address = Column(String(255))
    city = Column(String(100))
    state = Column(String(50))
    zip_code = Column(String(20))
    country = Column(String(100))

    parent_id = Column(Integer, ForeignKey('parents.parent_id'), nullable=False)
    parent = relationship("Parent", back_populates="address")
