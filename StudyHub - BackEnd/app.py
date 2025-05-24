from fastapi import FastAPI # type: ignore
from src.datalayer.dbconfig import configure_db
from src.api.configuration import configure_routes
from fastapi.middleware.cors import CORSMiddleware # type: ignore
from fastapi.staticfiles import StaticFiles # type: ignore


def create_app():
    app = FastAPI()
    app.mount("/src/media/uploads/images", StaticFiles(directory="src/media/uploads/images"), name="images")
    app.mount("/src/media/uploads/documents", StaticFiles(directory="src/media/uploads/documents"), name="documents")
    app.mount("/src/media/uploads/photo_profile", StaticFiles(directory="src/media/uploads/photo_profile"), name="photo_profile")
    configure_routes(app)
    configure_db(app)


    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # ⚠️ Em produção, substitua "*" por ["https://seusite.com"]
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    return app


app = create_app()