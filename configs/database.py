import os
from functools import lru_cache

from sqlalchemy import create_engine, event
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker, declarative_base
from configs.settings import get_settings

DATABASE_DIR = "./database"
os.makedirs(DATABASE_DIR, exist_ok=True)


GlobalsBase = declarative_base()

@lru_cache
def initialization_engine(database_name: str = "sqlite3.db"):
    database_path = os.path.join(DATABASE_DIR, database_name)
    return create_engine(
        f"sqlite:///{database_path}",
        connect_args={"check_same_thread": False}, 
    )


@lru_cache
def initialization_session(database: str = "sqlite3.db"):
    return sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=initialization_engine(database),
    )


def get_db_session():
    runtime_settings = get_settings()
    db = initialization_session(runtime_settings.DB_DATABASE)()
    try:
        yield db
    finally:
        db.close()

def initialize_database():
    """
    檢查並創建資料庫表。
    """
    from model.model import Products, CartItems, Cart

    engine = initialization_engine()  # 初始化資料庫引擎

    GlobalsBase.metadata.create_all(bind=engine)