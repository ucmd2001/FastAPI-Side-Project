from fastapi import FastAPI
import uvicorn
from fastapi.openapi.utils import get_openapi
from sqlalchemy.orm import Session
from sqlalchemy.sql import text

from configs.database import get_db_session, initialize_database
from apps.routers import routers

# 基本設定
TITLE = "WisdomGarden's Web Project"
DESCRIPTION = "WisdomGarden's Web Project"
VERSION = "0.0.1"

def app_factory() -> FastAPI:
    # 初始化 FastAPI 應用
    app = FastAPI(
        title=TITLE,
        debug=False,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )
    app.include_router(routers)

    initialize_database()


    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema
        openapi_schema = get_openapi(
            title=TITLE,
            version=VERSION,
            description=DESCRIPTION,
            routes=app.routes,
        )
        app.openapi_schema = openapi_schema
        return app.openapi_schema

    app.openapi = custom_openapi

    return app

app = app_factory()

async def try_phc_db_connect():
    try:
        db: Session = next(get_db_session())
        db.execute(text("SELECT 1"))
        print("Database connection successful")
        return True
    except Exception as e:
        print("Database connection failed:", e)
        raise e

@app.on_event("startup")
async def app_startup():
    await try_phc_db_connect()
    print("Simple FastAPI app is running!")

@app.on_event("shutdown")
async def shutdown_event():
    print("Application is shutting down.")


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)