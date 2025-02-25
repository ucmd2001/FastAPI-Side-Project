from sqlalchemy import Column, Integer, String, ForeignKey, Date, DECIMAL
from sqlalchemy.orm import relationship
from configs.database import GlobalsBase


class Cart(GlobalsBase):
    __tablename__ = "carts"

    id = Column(Integer, primary_key=True, index=True)
    checkout_date = Column(Date, nullable=False)
    cart_items = relationship("CartItems", back_populates="cart")


class Products(GlobalsBase):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    category = Column(String, nullable=False)
    price = Column(DECIMAL, nullable=False)
    cart_items = relationship("CartItems", back_populates="product")


class CartItems(GlobalsBase):
    __tablename__ = "cart_items"

    id = Column(Integer, primary_key=True, index=True)
    cart_id = Column(Integer, ForeignKey("carts.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    cart = relationship("Cart", back_populates="cart_items")
    product = relationship("Products", back_populates="cart_items")