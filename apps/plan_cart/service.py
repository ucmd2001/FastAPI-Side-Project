import re
from datetime import datetime

from fastapi import HTTPException, Depends
from decimal import Decimal
from sqlalchemy.orm import Session

from configs.database import get_db_session
from model.crud import ProductCrud
from apps.plan_cart.schema import Promotion, CartItem, Coupon, ParsedCartData


class PlanCartService:
    def __init__(self, db: Session = Depends(get_db_session)):
        self.db = db

    def data_precheck(self, input_data: str) -> ParsedCartData:
        """
        解析並檢查輸入數據，返回結構化數據。
        """
        sections = input_data.split("\n\n")

        if len(sections) < 2:
            raise ValueError(
                "Invalid input format. Expected at least 2 sections: cart items and checkout date."
            )

        promotions = []
        if len(sections) > 2 and "|" in sections[0]:
            for promo in sections[0].split("\n"):
                if promo.strip():
                    promo_parts = promo.split("|")
                    if len(promo_parts) != 3:
                        raise ValueError(f"Invalid promotion format: {promo}")
                    promo_date, rate, category = promo_parts
                    promotions.append(
                        Promotion(
                            date=datetime.strptime(
                                promo_date.strip(), "%Y.%m.%d"
                            ).date(),
                            rate=Decimal(rate.strip()),
                            category=category.strip(),
                        )
                    )
            cart_start_index = 1
        else:
            cart_start_index = 0

        cart_items = []
        for line in sections[cart_start_index].split("\n"):
            line = line.strip()
            if not line:
                continue
            match = re.match(r"(\d+)\*([^\:]+)\:(\d+\.\d+)", line)
            if not match:
                raise ValueError(f"Invalid cart item format: {line}")
            quantity, product_name, unit_price = match.groups()

            product = ProductCrud.get_product_by_name(self.db, product_name.strip())
            if not product:
                raise ValueError(
                    f"Product '{product_name.strip()}' not found in the database."
                )

            cart_items.append(
                CartItem(
                    product_name=product_name.strip(),
                    quantity=int(quantity),
                    unit_price=Decimal(unit_price.strip()),
                    category=str(product.category),
                )
            )

        try:
            checkout_date = datetime.strptime(
                sections[cart_start_index + 1].strip(), "%Y.%m.%d"
            ).date()
            if checkout_date > datetime.today().date():
                raise ValueError("Checkout date cannot be in the future.")
        except ValueError:
            raise ValueError(
                f"Invalid checkout date format: {sections[cart_start_index + 1].strip()}"
            )

        coupon = None
        if (
            len(sections) > cart_start_index + 2
            and sections[cart_start_index + 2].strip()
        ):
            coupon_parts = sections[cart_start_index + 2].strip().split(" ")
            if len(coupon_parts) != 3:
                raise ValueError(
                    f"Invalid coupon format: {sections[cart_start_index + 2].strip()}"
                )
            expiry_date, threshold, discount = coupon_parts
            expiry_date = datetime.strptime(expiry_date.strip(), "%Y.%m.%d").date()
            if checkout_date > expiry_date:
                raise ValueError("Coupon has expired.")
            coupon = Coupon(
                expiry_date=expiry_date,
                threshold=Decimal(threshold.strip()),
                discount=Decimal(discount.strip()),
            )

        return ParsedCartData(
            promotions=promotions,
            cart_items=cart_items,
            checkout_date=checkout_date,
            coupon=coupon,
        )

    def calculate_cart_total(self, parsed_data: ParsedCartData) -> Decimal:
        """
        計算購物車總金額。
        - parsed_data: 結構化數據，包括促銷資訊、購物車項目、結算日期、優惠券。
        """
        total_price = Decimal("0.00")

        for item in parsed_data.cart_items:
            item_total = item.unit_price * item.quantity

            for promo in parsed_data.promotions:
                if (
                    promo.date == parsed_data.checkout_date
                    and promo.category == item.category
                ):
                    item_total *= promo.rate

            total_price += item_total

        if parsed_data.coupon and total_price >= parsed_data.coupon.threshold:
            total_price -= parsed_data.coupon.discount

        return total_price.quantize(Decimal("0.01"))
