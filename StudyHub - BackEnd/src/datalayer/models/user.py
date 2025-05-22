from tortoise.models import Model
from tortoise import fields
from src.datalayer.models.base import ModelBase

class UserModel(ModelBase):
    name = fields.CharField(max_length=240)
    email = fields.CharField(max_length=240, unique=True)
    bio = fields.TextField(null=True)
    photo_profile =  fields.TextField(null=True)
    hashed_password = fields.TextField()
