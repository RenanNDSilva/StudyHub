from fastapi import HTTPException

def login_wrong_exception():
    raise HTTPException(status_code=404, detail="E-mail ou senha incorreto!")

def email_already_exists():
    raise HTTPException(status_code=400, detail="Esse e-mail já existe!")

def user_not_found():
    raise HTTPException(status_code=404, detail="Usuário não encontrado")

def access_denied():
    raise HTTPException(status_code=403, detail="Você não pode alterar o perfil de outro usuário!")

def access_denied_post():
    raise HTTPException(status_code=403, detail="Not authorized to update this post!")

def access_denied_comment():
    raise HTTPException(status_code=403, detail="Not authorized to update this comment")

def post_not_found():
    raise HTTPException(status_code=404, detail="Post not found")

def comment_not_found():
    raise HTTPException(status_code=404, detail="Comment not found")