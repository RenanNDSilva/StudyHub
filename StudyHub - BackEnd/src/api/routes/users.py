import os
import shutil
import uuid
from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from src.api.dtos.users import UserLogin, UserOut, UserRegistration, Token, UserUpdate
from src.datalayer.models.user import UserModel
from src.api.responses.user import access_denied, login_wrong_exception, email_already_exists, user_not_found
from src.datalayer.auth import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)
from datetime import timedelta


router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not Found"}},
)


@router.post('/register')
async def register(body: UserRegistration):
    
    email_exists = await UserModel.filter(email=body.email)
    if email_exists:
        raise email_already_exists()
        
    user = await UserModel.create(
        name = body.name,
        email = body.email,
        hashed_password = hash_password(body.password)
    )
    return {'created': user}


@router.post('/login', response_model=Token)
async def login(body: UserLogin):
    user = None
    
    try:
        user = await UserModel.get(email=body.email)
    except Exception:
        raise login_wrong_exception()

    if not verify_password(body.password, user.hashed_password):
        raise login_wrong_exception()
    
    token = create_access_token(
        data={"sub": body.email},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
        
    return {"access_token": token, "token_type": "bearer"}



@router.get('/get_users', response_model=list[UserOut])
async def get_users(current_user: UserModel = Depends(get_current_user)):
    users = await UserModel.all()
    return users


@router.get("/{user_id}")
async def get_user(user_id: int, current_user: UserModel = Depends(get_current_user)):
    try:
        return await UserModel.get(id=user_id)
    except Exception:
        raise user_not_found()


@router.put("/{user_id}")
async def update_user(user_id: int, 
                      name: str = Form(None),
                      bio: str = Form(None),
                      photo_profile: UploadFile = File(None),
                      current_user: UserModel = Depends(get_current_user)
                      ):
    if not user_id == current_user.id:
        raise access_denied()
    
    try:
        user = await UserModel.get(id=user_id)
    except Exception:
        raise user_not_found()

    user.name = name or user.name
    user.bio = bio or user.bio
    
    folder = "src/media/uploads/photo_profile"
    
    if photo_profile:
        if user.photo_profile:
            file_path = f"{folder}/{user.photo_profile}"
            if os.path.exists(file_path):
                    os.remove(file_path)
        
        ext = photo_profile.filename.split(".")[-1].lower()
        filename = f"{uuid.uuid4()}.{ext}"
        if ext in ["jpg", "jpeg", "png"]:
            os.makedirs(folder, exist_ok=True)
            file_path_save = f"{folder}/{filename}"
            user.photo_profile = filename
            with open(file_path_save, "wb") as f:
                shutil.copyfileobj(photo_profile.file, f)
        else:
            raise HTTPException(status_code=400, detail="Invalid file type. Allowed types: jpg, jpeg, png.")

        
    await user.save()
    return user


@router.delete("/{user_id}")
async def delete_user(user_id: int, current_user: UserModel = Depends(get_current_user)):
    if not user_id == current_user.id:
        raise access_denied()
    
    try:
        user = await UserModel.get(id=user_id)
        await user.delete()
        return {"detail": "Usuário deletado com sucesso."}
    except Exception:
        raise user_not_found()


@router.get('/get-mini-user/{user_id}')
async def get_mini_user(user_id: int, current_user: UserModel = Depends(get_current_user)):
    try:
        user = await UserModel.get(id=user_id).values('id', 'name', 'photo_profile')
    except Exception:
        raise user_not_found()
    return user


@router.get('/get-user-id/{email}')
async def get_user_id(email: str):
    user = await UserModel.get_or_none(email=email)
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return {"id": user.id}