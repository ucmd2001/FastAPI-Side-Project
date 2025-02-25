import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from configs.database import GlobalsBase
from model.crud import ProductCrud


@pytest.fixture(scope="session")
def test_db():
    """
    使用 SQLite in-memory 數據庫作為測試數據庫。
    """
    engine = create_engine("sqlite:///:memory:")
    GlobalsBase.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    # 插入測試數據
    products = [
        {"name": "ipad", "category": "電子", "price": 2399.00},
        {"name": "顯示器", "category": "電子", "price": 1799.00},
        {"name": "啤酒", "category": "酒類", "price": 25.00},
        {"name": "麵包", "category": "食品", "price": 9.00},
    ]
    for product in products:
        ProductCrud.add_product(session, product)

    yield session
    session.close()


@pytest.fixture(scope="function")
def test_db(tmp_path):
    """
    使用獨立的測試數據庫文件。
    測試結束後刪除該文件。
    """
    test_db_path = tmp_path / "test.sqlite3"
    engine = create_engine(f"sqlite:///{test_db_path}")
    GlobalsBase.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    yield session  # 測試結束時，釋放 session
    session.close()
