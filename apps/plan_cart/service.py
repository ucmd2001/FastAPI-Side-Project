import re
from datetime import datetime, date
from typing import Optional

from fastapi import HTTPException, Depends
from decimal import Decimal
from sqlalchemy.orm import Session

from configs.database import get_db_session
from model.crud import ProductCrud
from apps.plan_cart.schema import Promotion, CartItem, Coupon, ParsedCartData


class PlanCartService:
    def __init__(self, db: Session = Depends(get_db_session)):
        self.db = db

    async def parse_promotions(self, section: str) -> list[Promotion]:
        """解析促銷資訊"""
        promotions = []
        for promo in section.split("\n"):
            try:
                promo_date, rate, category = map(str.strip, promo.split("|"))
                promotions.append(
                    Promotion(
                        date=datetime.strptime(promo_date, "%Y.%m.%d").date(),
                        rate=Decimal(rate),
                        category=category,
                    )
                )
            except ValueError:
                raise ValueError(f"Invalid promotion format: {promo}")
        return promotions

    async def parse_cart_items(self, section: str, db: Session) -> list[CartItem]:
        """解析購物車內容，並查詢 DB 取得類別資訊"""
        cart_items = []
        product_names = {
            line.split("*")[1].split(":")[0].strip() for line in section.split("\n")
        }

        # 🚀 **批次查詢所有商品，減少 DB 查詢次數**
        products = {
            p.name: p
            for p in ProductCrud.get_all_products(db)
            if p.name in product_names
        }

        for line in section.split("\n"):
            match = re.match(r"(\d+)\*([^\:]+)\:(\d+\.\d+)", line)
            if not match:
                raise ValueError(f"Invalid cart item format: {line}")

            quantity, product_name, unit_price = match.groups()
            product_name = product_name.strip()

            product = products.get(product_name)
            if not product:
                raise ValueError(f"Product '{product_name}' not found in the database.")

            cart_items.append(
                CartItem(
                    product_name=product_name,
                    quantity=int(quantity),
                    unit_price=Decimal(unit_price),
                    category=product.category,
                )
            )
        return cart_items

    async def parse_checkout_date(self, section: str) -> date:
        """解析結算日期"""
        try:
            checkout_date = datetime.strptime(section.strip(), "%Y.%m.%d").date()
            if checkout_date > datetime.today().date():
                raise ValueError("Checkout date cannot be in the future.")
            return checkout_date
        except ValueError:
            raise ValueError(f"Invalid checkout date format: {section}")

    async def parse_coupon(self, section: str, checkout_date: date) -> Optional[Coupon]:
        """解析優惠券"""
        try:
            expiry_date, threshold, discount = map(str.strip, section.split(" "))
            expiry_date = datetime.strptime(expiry_date, "%Y.%m.%d").date()
            if checkout_date > expiry_date:
                raise ValueError("Coupon has expired.")
            return Coupon(
                expiry_date=expiry_date,
                threshold=Decimal(threshold),
                discount=Decimal(discount),
            )
        except ValueError:
            raise ValueError(f"Invalid coupon format: {section}")

    async def data_precheck(self, input_data: str) -> ParsedCartData:
        """
        解析並檢查輸入數據，返回結構化數據。
        """
        t_start = datetime.now()

        sections = [
            section.strip() for section in input_data.split("\n\n") if section.strip()
        ]
        if len(sections) < 2:
            raise ValueError("Invalid input format. Expected at least 2 sections.")

        checkout_date = None
        promotions_section = None
        cart_section = None
        coupon_section = None

        for section in sections:
            lines = section.split("\n")

            if "|" in section and len(lines[0].split("|")) == 3:
                promotions_section = section
            elif re.match(r"^\d+\*", lines[0]):
                cart_section = section
            elif re.match(r"^\d{4}\.\d{2}\.\d{2}$", section):
                checkout_date = section
            elif len(lines[0].split(" ")) == 3:
                coupon_section = section

        if not checkout_date:
            raise ValueError("Missing checkout date.")

        promotions = (
            await self.parse_promotions(promotions_section)
            if promotions_section
            else []
        )
        cart_items = (
            await self.parse_cart_items(cart_section, self.db) if cart_section else []
        )
        checkout_date = (
            await self.parse_checkout_date(checkout_date) if checkout_date else None
        )
        coupon = (
            await self.parse_coupon(coupon_section, checkout_date)
            if coupon_section
            else None
        )

        if not checkout_date:
            raise ValueError("Missing checkout date.")

        print("Parsing time:", datetime.now() - t_start)

        return ParsedCartData(
            promotions=promotions,
            cart_items=cart_items,
            checkout_date=checkout_date,
            coupon=coupon,
        )

    async def calculate_cart_total(self, parsed_data: ParsedCartData) -> Decimal:
        """
        計算購物車總金額。
        - parsed_data: 結構化數據，包括促銷資訊、購物車項目、結算日期、優惠券。
        """
        total_price = sum(
            (item.unit_price * item.quantity)
            * (
                next(
                    (
                        promo.rate
                        for promo in parsed_data.promotions
                        if promo.date == parsed_data.checkout_date
                        and promo.category == item.category
                    ),
                    1,
                )
            )
            for item in parsed_data.cart_items
        )

        if parsed_data.coupon and total_price >= parsed_data.coupon.threshold:
            total_price -= parsed_data.coupon.discount

        return total_price.quantize(Decimal("0.01"))
