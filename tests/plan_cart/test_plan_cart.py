import pytest
from decimal import Decimal
from datetime import datetime
from unittest.mock import MagicMock
from apps.plan_cart.service import PlanCartService
from apps.plan_cart.schema import ParsedCartData, Promotion, CartItem, Coupon


@pytest.fixture
def mock_db():
    """
    提供一個模擬的資料庫對象。
    """
    mock = MagicMock()
    return mock


@pytest.fixture
def service(mock_db):
    """
    提供 PlanCartService 的實例。
    """
    return PlanCartService(mock_db)


def test_data_precheck_with_valid_data(service):
    input_data = (
        "2015.11.11|0.7|電子\n\n"
        "1*ipad:2399.00\n1*顯示器:1799.00\n\n"
        "2015.11.11\n\n"
        "2016.3.2 1000 200"
    )

    parsed_data = service.data_precheck(input_data)

    assert len(parsed_data.promotions) == 1
    assert parsed_data.promotions[0].date == datetime(2015, 11, 11).date()
    assert parsed_data.promotions[0].rate == Decimal("0.7")
    assert parsed_data.promotions[0].category == "電子"
    assert len(parsed_data.cart_items) == 2
    assert parsed_data.cart_items[0].product_name == "ipad"
    assert parsed_data.cart_items[0].quantity == 1
    assert parsed_data.cart_items[0].unit_price == Decimal("2399.00")
    assert parsed_data.checkout_date == datetime(2015, 11, 11).date()
    assert parsed_data.coupon.expiry_date == datetime(2016, 3, 2).date()
    assert parsed_data.coupon.threshold == Decimal("1000")
    assert parsed_data.coupon.discount == Decimal("200")


def test_calculate_cart_total(service):
    parsed_data = ParsedCartData(
        promotions=[
            Promotion(date=datetime(2015, 11, 11).date(), rate=Decimal("0.7"), category="電子")
        ],
        cart_items=[
            CartItem(product_name="ipad", quantity=1, unit_price=Decimal("2399.00"), category="電子"),
            CartItem(product_name="顯示器", quantity=1, unit_price=Decimal("1799.00"), category="電子"),
        ],
        checkout_date=datetime(2015, 11, 11).date(),
        coupon=Coupon(expiry_date=datetime(2016, 3, 2).date(), threshold=Decimal("1000"), discount=Decimal("200")),
    )

    result = service.calculate_cart_total(parsed_data)

    assert result == Decimal("2738.60")
