from importlib.metadata import files
import os
import shutil
from typing import List, Optional
import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from src.api.responses.user import access_denied_comment, access_denied_post, comment_not_found, post_not_found
from src.api.dtos.post import PostRegistration
from src.datalayer.auth import get_current_user
from src.datalayer.models.post import PostCommentModel, PostLikeModel, PostModel
from src.datalayer.models.user import UserModel
from tortoise.exceptions import DoesNotExist



router = APIRouter(
    prefix="/posts",
    tags=["posts"],
    responses={404: {"description": "Not Found"}},
)


@router.post("/create")
async def create_post(
    message: str = Form(None),
    archives: Optional[List[UploadFile]] = File(None),  # Tornando arquivos opcionais
    current_user: UserModel = Depends(get_current_user)
):
    saved_archives = []
    
    if archives:  # Verifica se arquivos foram enviados
        for file in archives:
            ext = file.filename.split(".")[-1].lower()
            filename = f"{uuid.uuid4()}.{ext}"

            if ext in ["jpg", "jpeg", "png", "gif", "webp"]:
                folder = "src/media/uploads/images"
                os.makedirs(folder, exist_ok=True)
                filepath = f"{folder}/{filename}"
                saved_archives.append(f"/{filename}")
            elif ext == "pdf":
                folder = "src/media/uploads/documents"
                os.makedirs(folder, exist_ok=True)
                filepath = f"{folder}/{filename}"
                saved_archives.append(f"/{filename}")
            else:
                continue

            with open(filepath, "wb") as f:
                shutil.copyfileobj(file.file, f)

    post = await PostModel.create(
        user=current_user,
        message=message,
        archives=saved_archives 
    )
    return post



@router.get("/all-posts")
async def get_posts(current_user: UserModel = Depends(get_current_user)):
    return await PostModel.all()


@router.get("/{post_id}")
async def get_post(post_id: int, current_user: UserModel = Depends(get_current_user)):
    try:
        post = await PostModel.get(id=post_id)
        return post
    except Exception:
        raise post_not_found()
    
  
@router.get("/user/{user_id}")
async def get_user_posts(user_id: int, current_user: UserModel = Depends(get_current_user)):
    posts = await PostModel.filter(user=user_id)
    if not posts:
        raise post_not_found()

    return posts


@router.get("/my-posts")
async def get_my_posts(current_user: UserModel = Depends(get_current_user)):
    posts = await PostModel.filter(user=current_user.id)
    if not posts:
        raise post_not_found()

    return posts


@router.put("/{post_id}")
async def update_post(post_id: int,
                      message: str = Form(None),
                      archives: Optional[List[UploadFile]] = File(None), 
                      current_user: UserModel = Depends(get_current_user)
                      ):
    try:
        post = await PostModel.filter(id=post_id).select_related("user").first()
        
        if post.user.id != current_user.id:
            raise access_denied_post()

        if message:
            post.message = message  # Atualiza a mensagem    

        if archives:
            # Remove arquivos antigos se forem fornecidos novos
            for old_file in post.archives:

                ext = old_file.split(".")[-1].lower()

                if ext in ["jpg", "jpeg", "png", "gif", "webp"]:
                    file_path = f"src/media/uploads/images/{old_file}"
                elif ext == "pdf":
                    file_path = f"src/media/uploads/documents/{old_file}"

                if os.path.exists(file_path):
                    os.remove(file_path)

            # Adiciona novos arquivos
            saved_archives = []
            for file in archives:
                ext = file.filename.split(".")[-1].lower()
                filename = f"{uuid.uuid4()}.{ext}"
                folder = "src/media/uploads/images" if ext in ["jpg", "jpeg", "png", "gif", "webp"] else "src/media/uploads/documents"
                os.makedirs(folder, exist_ok=True)
                filepath = f"{folder}/{filename}"
                saved_archives.append(f"{filename}")
                with open(filepath, "wb") as f:
                    shutil.copyfileobj(file.file, f)

            post.archives = saved_archives

        await post.save()
        return post
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"{e}")


@router.delete("/{post_id}")
async def delete_post(post_id: int, current_user: UserModel = Depends(get_current_user)):
    try:
        post = await PostModel.filter(id=post_id).select_related("user").first()
        
        if post.user.id != current_user.id:
            raise access_denied_post()

        # Remover arquivos
        if post.archives:
            # Remove arquivos antigos se forem fornecidos novos
            for old_file in post.archives:

                ext = old_file.split(".")[-1].lower()

                if ext in ["jpg", "jpeg", "png", "gif", "webp"]:
                    file_path = f"src/media/uploads/images/{old_file}"
                elif ext == "pdf":
                    file_path = f"src/media/uploads/documents/{old_file}"
                
                print(file_path)
                if os.path.exists(file_path):
                    os.remove(file_path)

        await post.delete()
        return {"detail": "Post deleted successfully"}
    except Exception:
        raise post_not_found()
    
    

@router.post("/{post_id}/like")
async def like_post(
    post_id: int,
    current_user: UserModel = Depends(get_current_user)
):

    post = await PostModel.get(id = post_id)
    try:
        like_exists = await PostLikeModel.get(user_id=current_user.id, post_id=post_id)
        await like_exists.delete()
        post.likes_count -= 1
        await post.save()


    except DoesNotExist as e:
        await PostLikeModel.create(
            user_id = current_user.id,
            post_id = post_id
        )
        post.likes_count += 1
        await post.save()
        

    return {"likes_count": post.likes_count}


@router.post('/{post_id}/comment')
async def comment_post(
    post_id: int,
    message: str,
    current_user: UserModel = Depends(get_current_user),
):
    try:
        post = await PostModel.get(id = post_id)
    except DoesNotExist as e:
        raise post_not_found()
    
    comment = await PostCommentModel.create(
        user_id = current_user.id,
        post_id = post_id,
        message = message
    )

    post.comments_count += 1
    await post.save()

    return {"comment": comment}


@router.put('/{post_id}/comments')
async def update_post_comments(
    comment_id: int,
    message: str,
    current_user: UserModel = Depends(get_current_user),
):
    try:
        comment = await PostCommentModel.get(id=comment_id)
    except DoesNotExist:
        raise comment_not_found()

    # Verifica se o comentário pertence ao usuário
    if comment.user_id != current_user.id:
        raise access_denied_comment()
    
    comment.message = message
    await comment.save()

    return comment



@router.delete("/comment/{comment_id}")
async def delete_comment(comment_id: int, current_user: UserModel = Depends(get_current_user)):
    try:
        comment = await PostCommentModel.filter(id=comment_id).select_related("post").first()
        print(comment.post.id)
    except DoesNotExist:
        raise comment_not_found()

    # Verifica se o comentário pertence ao usuário
    if comment.user_id != current_user.id:
        raise access_denied_comment()

    post = await PostModel.get(id=comment.post.id)

    # Remove o comentário
    await comment.delete()

    post.comments_count -= 1
    await post.save()

    return {"detail": "Comment deleted successfully"}


@router.get('/{post_id}/comments')
async def get_post_comments(
    post_id: int,
    current_user: UserModel = Depends(get_current_user),
):
    return await PostCommentModel.filter(post_id = post_id).order_by('-created_at')