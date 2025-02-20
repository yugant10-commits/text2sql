from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.api.routes import chat
from app.config.settings import settings

def create_app() -> FastAPI:
    app = FastAPI(title=settings.APP_NAME)
    
    # Mount static files
    app.mount("/static", StaticFiles(directory="app/static"), name="static")
    
    # Templates setup
    templates = Jinja2Templates(directory="app/templates")
    
    # Root route
    @app.get("/")
    async def home(request: Request):
        return templates.TemplateResponse("index.html", {"request": request})
    
    # Include routers
    app.include_router(chat.router)
    
    return app

app = create_app()