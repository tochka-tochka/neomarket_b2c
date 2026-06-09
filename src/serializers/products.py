from rest_framework import serializers


class SKUSerializer(serializers.Serializer):

    id = serializers.UUIDField()
    name = serializers.CharField(required=False, allow_null=True)
    price = serializers.IntegerField(min_value=0)
    old_price = serializers.IntegerField(min_value=0, allow_null=True, required=False)
    available_quantity = serializers.IntegerField(min_value=0)
    attributes = serializers.DictField(required=False, default=dict)
    images = serializers.ListField(required=False, default=list)


class ProductCardSerializer(serializers.Serializer):

    id = serializers.UUIDField()
    name = serializers.CharField()
    slug = serializers.CharField(required=False, allow_null=True)
    description = serializers.CharField()
    min_price = serializers.IntegerField(min_value=0)
    old_price = serializers.IntegerField(min_value=0, allow_null=True, required=False)
    has_stock = serializers.BooleanField()
    images = serializers.ListField(default=list)
    attributes = serializers.DictField(required=False, default=dict)
    skus = SKUSerializer(many=True)

    category = serializers.DictField(required=False, allow_null=True)
    rating = serializers.FloatField(required=False, allow_null=True)
    reviews_count = serializers.IntegerField(required=False, default=0)
    seller = serializers.DictField(required=False, allow_null=True)