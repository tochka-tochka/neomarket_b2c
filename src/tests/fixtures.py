import pytest

from src.models.orders import Address, Order, OrderItem, OrderStatus, PaymentMethod

@pytest.fixture
def test_address(test_user):
    address = Address.objects.create(
        country="Россия",
        city="Екатеринбург",
        street="Ленина",
        building="1",
        apartment="1",
        postal_code="111111",
        recipient_name="recipient",
        recipient_phone="+79999999999",
        comment="rwqjflgtj",
        buyer=test_user,
    )
    return address


@pytest.fixture
def test_payment_method(test_user):
    payment_method = PaymentMethod.objects.create(
        type="CARD", card_last4="1111", card_brand="VISA", buyer=test_user
    )
    return payment_method
