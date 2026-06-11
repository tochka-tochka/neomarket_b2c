from rest_framework import serializers


class CatalogProductCardSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()
    slug = serializers.CharField(required=False, allow_null=True)
    category = serializers.DictField(required=False, allow_null=True)
    min_price = serializers.IntegerField(min_value=0)
    old_price = serializers.IntegerField(min_value=0, allow_null=True, required=False)
    has_stock = serializers.BooleanField()
    rating = serializers.FloatField(min_value=0, max_value=5, allow_null=True, required=False)
    reviews_count = serializers.IntegerField(min_value=0, default=0)
    images = serializers.ListField(default=list)
    seller = serializers.DictField(required=False, allow_null=True)


class PaginatedCatalogProductsSerializer(serializers.Serializer):
    items = CatalogProductCardSerializer(many=True)
    total_count = serializers.IntegerField()
    limit = serializers.IntegerField()
    offset = serializers.IntegerField()