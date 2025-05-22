from pydantic import BaseModel
from fastapi import UploadFile, File, Form


class PostRegistration(BaseModel):
    message: str
    archives: list[UploadFile] = File(...)