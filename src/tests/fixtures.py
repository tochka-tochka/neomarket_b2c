import pytest
import uuid

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


@pytest.fixture
def test_order(test_user, test_address, test_payment_method):
    order = Order.objects.create(
        buyer=test_user,
        number="ORD-SKU-123",
        status=OrderStatus.PAID,
        address=test_address,
        payment_method=test_payment_method,
    )
    OrderItem.objects.create(
        order=order,
        sku_id=str(uuid.uuid4()),
        product_id=str(uuid.uuid4()),
        name="Product 1",
        quantity=2,
        unit_price=100.00,
        line_total=200.00,
        image_url="http://example.com/image1.jpg",
    )
    OrderItem.objects.create(
        order=order,
        sku_id=str(uuid.uuid4()),
        product_id=str(uuid.uuid4()),
        name="Product 2",
        quantity=1,
        unit_price=50.00,
        line_total=50.00,
        image_url="http://example.com/image2.jpg",
    )
    return order
