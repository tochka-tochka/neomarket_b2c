from rest_framework import serializers


class CartItemSerializer(serializers.Serializer):

    sku_id = serializers.UUIDField()
    product_id = serializers.UUIDField(allow_null=True, required=False)
    name = serializers.CharField()
    quantity = serializers.IntegerField(min_value=1)
    unit_price = serializers.IntegerField(min_value=0, help_text="Актуальная цена за единицу, копейки")
    line_total = serializers.IntegerField(help_text="unit_price * quantity")
    available_quantity = serializers.IntegerField(min_value=0)
    is_available = serializers.BooleanField()

    sku_code = serializers.CharField(required=False, allow_null=True)
    unit_price_at_add = serializers.IntegerField(required=False, allow_null=True, help_text="Цена на момент добавления")
    image = serializers.DictField(required=False, allow_null=True)


class CartResponseSerializer(serializers.Serializer):

    id = serializers.UUIDField(help_text="ID корзины (или сессии)")
    items = CartItemSerializer(many=True)
    items_count = serializers.IntegerField(help_text="Сумма quantity по всем строкам")
    subtotal = serializers.IntegerField(help_text="Сумма line_total, копейки")
    is_valid = serializers.BooleanField(
        help_text="true если все позиции is_available и количество не превышает остаток")
    updated_at = serializers.DateTimeField()


class CartItemCreateSerializer(serializers.Serializer):

    sku_id = serializers.UUIDField()
    quantity = serializers.IntegerField(min_value=1)


class CartItemUpdateSerializer(serializers.Serializer):

    quantity = serializers.IntegerField(min_value=1)