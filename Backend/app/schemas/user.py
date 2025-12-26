from datetime import datetime
from enum import Enum
import re
from pydantic import BaseModel, EmailStr, field_validator


class UserRole(str, Enum):
    USER = "USER"
    AGENT = "AGENT"
    ADMIN = "ADMIN"


class UserCreateSchema(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: str
    password: str

    @field_validator('phone_number')
    def validate_phone(cls, v: str) -> str:
        s = re.sub(r'[^\d+]', '', v)
        digits = re.sub(r'\D', '', s)
        if len(digits) < 7 or len(digits) > 15:
            raise ValueError('phone_number must contain 7-15 digits')
        return v


class UserLoginSchema(BaseModel):
    email: EmailStr
    password: str


class UserResponseSchema(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: str | None
    role: UserRole
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class UserUpdateSchema(BaseModel):
    first_name: str | None
    last_name: str | None
    email: EmailStr | None
    phone_number: str | None
    password: str | None

