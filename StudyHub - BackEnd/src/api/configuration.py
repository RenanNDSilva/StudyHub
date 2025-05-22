from fastapi import FastAPI
from src.api.routes import post
from src.api.routes import users

def configure_routes(app: FastAPI):
    app.include_router(users.router)
    app.include_router(post.router)