from pydantic import BaseModel,field_validator,ConfigDict
from datetime import datetime
from typing import Optional
from pathlib import Path
from uuid import UUID
import uuid

class PictureIn(BaseModel):
    pic_path:str

    @field_validator('pic_path')
    @classmethod
    def validate_pic_path(cls, value:str)->str:
        allowed_extensions = ['.jpg','.jpeg','.png']

        ext = Path(value).suffix.lower()
        if ext not in allowed_extensions:
            raise ValueError(f"Unsupported file extension: {ext}")

        return value

class ProfilePicOut(BaseModel):
    pic_id: UUID
    original_name:str
    saved_as:str
    folder:str
    size:int
    uploaded_at:datetime

    model_config = ConfigDict(
        from_attributes=True
    )




