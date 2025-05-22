from fastapi import APIRouter
from src.datalayer.models.user import UserModel


router = APIRouter(
    prefix="/me",
    tags=["me"],
    responses={404: {"description": "Not Found"}},
)


@router.post('/')
async def my_informations():
    return ...