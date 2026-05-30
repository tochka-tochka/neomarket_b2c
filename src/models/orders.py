from uuid import uuid4

from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from django.db.models.fields.related import ForeignKey


class PaymentMethodType(models.TextChoices):
    CARD = "CARD"
    SBP = "SBP"
    WALLET = "WALLET"


class CardBrands(models.TextChoices):
    VISA = "VISA"
    MASTERCARD = "MASTERCARD"
    MIR = "MIR"


class PaymentMethod(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    type = models.TextField(choices=PaymentMethodType)
    card_last4 = models.TextField(
        max_length=4,
        validators=[
            RegexValidator(
                regex=r"^[0-9]{4}$",
                message="Нужно ввести последние 4 цифры номера карты",
            )
        ],
    )
    card_brand = models.TextField(choices=CardBrands)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    buyer = ForeignKey(User, on_delete=models.CASCADE, related_name="payment_methods")

    class Meta:
        db_table = "payment_methods"


class Address(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    country = models.CharField(max_length=100)
    region = models.CharField(max_length=200, null=True, blank=True)
    city = models.CharField(max_length=200)
    street = models.CharField(max_length=200)
    building = models.CharField(max_length=50)
    apartment = models.CharField(max_length=50)
    postal_code = models.CharField(max_length=20)
    recipient_name = models.CharField(max_length=200)
    recipient_phone = models.CharField(
        validators=[
            RegexValidator(
                regex=r"^\+?[0-9]{10,15}$",
                message="Номер телефона должен быть в формате: +79999999999",
            )
        ],
    )
    is_default = models.BooleanField(default=False)
    comment = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    buyer = ForeignKey(User, on_delete=models.CASCADE, related_name="addresses")

    class Meta:
        db_table = "addresses"


class OrderStatus(models.TextChoices):
    CREATED = "CREATED"
    PAID = "PAID"
    ASSEMBLING = "ASSEMBLING"
    DELIVERING = "DELIVERING"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"
    CANCEL_PENDING = "CANCEL_PENDING"


class Order(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    number = models.CharField()
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    status = models.TextField(choices=OrderStatus)
    delivery_cost = models.IntegerField(default=0)
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True)
    payment_method = models.ForeignKey(
        PaymentMethod, on_delete=models.SET_NULL, null=True
    )
    comment = models.TextField(null=True, blank=True)
    cancel_reason = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "orders"


class OrderItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    sku_id = models.UUIDField()
    product_id = models.UUIDField()
    name = models.CharField()
    sku_code = models.CharField(null=True, blank=True)
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    unit_price = models.IntegerField(validators=[MinValueValidator(0)])
    line_total = models.IntegerField(validators=[MinValueValidator(1)])
    image_url = models.CharField()
    order = ForeignKey(Order, on_delete=models.CASCADE, related_name="items")

    class Meta:
        db_table = "order_items"


class StatusHistory:
    status = models.TextField(choices=OrderStatus)
    changed_at = models.DateTimeField(auto_now_add=True)
    comment = models.TextField(null=True, blank=True)
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="status_history"
    )

    class Meta:
        db_table = "status_history"

class OrderOperations(models.Model):
    idempotency_key = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)

    class Meta:
        db_table = "order_opearions"