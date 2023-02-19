from pydantic import BaseModel, ValidationError, validator, EmailStr
from errors import HttpError
import re
from typing import Any, Dict, Optional, Type

password_regex = re.compile(
    "^(?=.*[a-z_])(?=.*[a-z_])(?=.*\d)(?=.*[@$!%*#?&_])[A-Za-z\d@$!#%*?&_]{8,50}$"
)


class CreatePost(BaseModel):
    title: str
    description: str


class CreateUser(BaseModel):
    username: str
    password: str

    @validator('password')
    def validate_password(cls, value: str):
        if not re.search(password_regex, value) and len(value) <= 7:
            raise ValueError('password is to easy or/and/ must contain 7 chars or more')
        return value


SCHEMA_TYPE = Type[CreatePost] | Type[CreateUser]


def validate(schema: SCHEMA_TYPE, data: Dict[str, Any], exclude_none: bool = True):
    try:
        validatet = schema(**data).dict(exclude_none=exclude_none)
        return validatet
    except ValidationError as er:
        raise HttpError(status_code=400, message=er.errors())
