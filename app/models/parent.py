import uuid
from pydantic import BaseModel, EmailStr, constr, Field
from typing import Optional


class Parent(BaseModel):
    id: str = Field(default_factory=uuid.uuid4, alias="_id")
    name: constr(strip_whitespace=True, min_length=1)
    email: EmailStr
    phone_number: constr(strip_whitespace=True, min_length=1)

    class Config:
        schema_extra = {
            "example": {
                "_id": "123e4567-e89b-12d3-a456-426614174000",  # Example UUID
                "name": "Jane Doe",
                "email": "janedoe@example.com",
                "phone_number": "555-555-5555"
            }
        }


class ParentUpdate(BaseModel):
    name: Optional[constr(strip_whitespace=True, min_length=1)]
    email: Optional[EmailStr]
    phone_number: Optional[constr(strip_whitespace=True, min_length=1)]

    class Config:
        schema_extra = {
            "example": {
                "name": "Jane Smith",  # Updated name
                "email": "janesmith@example.com",  # Updated email
                "phone_number": "555-555-1234"  # Updated phone number
            }
        }


# Example usage:
parent_update_data = {
    "name": "Jane Smith",
    "email": "janesmith@example.com",
    "phone_number": "555-555-1234"
}

parent_update = ParentUpdate(**parent_update_data)
print(parent_update)
