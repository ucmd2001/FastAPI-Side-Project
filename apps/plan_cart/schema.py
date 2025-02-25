from pydantic import BaseModel, Field
from decimal import Decimal
from typing import List, Optional
import datetime

class CheckoutInput(BaseModel):
    data: str

class CartOutput(BaseModel):
    total_price: Decimal

class Promotion(BaseModel):
    date: datetime.date
    rate: Decimal
    category: str


class CartItem(BaseModel):
    product_name: str
    quantity: int
    unit_price: Decimal
    category: str  # 商品類別


class Coupon(BaseModel):
    expiry_date: datetime.date
    threshold: Decimal
    discount: Decimal


class ParsedCartData(BaseModel):
    promotions: List[Promotion] = Field(default_factory=list)
    cart_items: List[CartItem] = Field(default_factory=list)
    checkout_date: datetime.date
    coupon: Optional[Coupon]

