import uvicorn
from app.config.settings import settings

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        reload_includes=["*.html", "*.css", "*.js"],
        reload_dirs=["app"]
    )