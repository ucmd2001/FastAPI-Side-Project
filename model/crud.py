from sqlalchemy.orm import Session
from .model import Products


class ProductCrud:
    @staticmethod
    def get_product_by_name(db: Session, name: str):
        """
        根據商品名稱查詢商品信息。
        """
        return db.query(Products).filter(Products.name == name).first()

    @staticmethod
    def get_all_products(db: Session):
        """
        查詢所有商品
        """
        return db.query(Products).all()

    @staticmethod
    def add_product(db: Session, product: dict):
        """
        添加單個商品到資料庫
        - product: 商品數據，格式如 {"name": "ipad", "category": "電子", "price": 2399.00}
        """
        new_product = Products(**product)
        db.add(new_product)
        db.commit()
        db.refresh(new_product)
        return new_product

    @staticmethod
    def bulk_add_products(db: Session, products: list[dict]):
        """
        批量添加多個商品到資料庫
        - products: 商品數據列表，格式如：
          [{"name": "ipad", "category": "電子", "price": 2399.00}, {...}]
        """
        new_products = [Products(**product) for product in products]
        db.add_all(new_products)
        db.commit()
        return new_products