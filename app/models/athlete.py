import uuid
from datetime import date
from pydantic import BaseModel, Field, constr
from typing import Optional
from parent import Parent
from typing import Literal


# Pydantic model for the Athlete.
class Athlete(BaseModel):
    id: str = Field(default_factory=uuid.uuid4, alias="_id")
    full_name: constr(strip_whitespace=True, min_length=1)  # A non-empty string
    date_of_birth: date  # A date object
    gender: Literal['male', 'female']
    returner_status: Literal['new', 'returner']
    parent: Parent  # This uses the Parent model defined above

    class Config:
        schema_extra = {
            "example": {
                "full_name": "Don Quixote",
                "date_of_birth": "1968-06-22",
                "gender": "male",
                "returner_status": "new",
                "parent": {
                    "name": "Jane Doe",
                    "email": "janedoe@example.com",
                    "phone_number": "555-555-5555"
                }
            }
        }


class AthleteUpdate(BaseModel):
    full_name: Optional[constr(strip_whitespace=True, min_length=1)]
    date_of_birth: Optional[date]
    gender: Optional[Literal['male', 'female']]
    returner_status: Optional[Literal['new', 'returner']]
    parent: Optional[Parent]

    class Config:
        schema_extra = {
            "example": {
                "_id": "123e4567-e89b-12d3-a456-426614174000",  # UUIDs should be unique, this is just a placeholder
                "full_name": "Don Quixote",
                "date_of_birth": "1968-06-22",
                "gender": "male",
                "returner_status": "new",
                "parent": {
                    "name": "Jane Doe",
                    "email": "janedoe@example.com",
                    "phone_number": "555-555-5555"
                }
            }
        }
