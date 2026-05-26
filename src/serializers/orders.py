from rest_framework import serializers

from src.models.orders import Address, Order, OrderItem, PaymentMethod, StatusHistory


class PaymentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethod
        fields = ["id", "type", "card_list4", "card_brand", "is_default", "created_at"]


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = [
            "id",
            "country",
            "region",
            "city",
            "street",
            "building",
            "apartment",
            "postal_code",
            "recipient_name",
            "recipient_phone",
            "is_default",
            "comment",
            "created_at",
        ]


class StatusHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = StatusHistory
        fields = ["status", "changed_at", "reason"]


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = [
            "sku_id",
            "product_id",
            "name",
            "sku_code",
            "quantity",
            "unit_price",
            "line_total",
            "image_url",
        ]


class OrderSerializer(serializers.ModelSerializer):
    buyer_id = serializers.UUIDField(source="auth_user.id", read_only=True)
    status_history = StatusHistorySerializer(read_only=True, many=True)
    items = OrderItemSerializer(read_only=True, many=True)
    subtotal = serializers.SerializerMethodField()
    total = serializers.SerializerMethodField()
    address = AddressSerializer(read_only=True)
    payment_method = PaymentMethodSerializer(read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "number",
            "buyer_id",
            "status",
            "status_history",
            "items",
            "subtotal",
            "delivery_cost",
            "total",
            "address",
            "payment_method",
            "comment",
            "cancel_reason",
            "created_at",
            "paid_at",
            "delivered_at",
        ]

    def get_subtotal(self, obj):
        return sum(item.line_total for item in obj.items.all())
    
    def get_total(self, obj):
        subtotal = self.get_subtotal(obj)
        
        delivery_cost = obj.delivery_cost or 0 
        
        return subtotal + delivery_cost
