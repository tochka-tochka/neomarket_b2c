from rest_framework import serializers


class B2BEventSerializer(serializers.Serializer):
    event_type = serializers.ChoiceField(choices=[
        'PRODUCT_BLOCKED', 'PRODUCT_HARD_BLOCKED', 'PRODUCT_DELETED',
        'SKU_OUT_OF_STOCK', 'SKU_BACK_IN_STOCK', 'PRICE_CHANGED',
    ])
    idempotency_key = serializers.UUIDField()
    occurred_at = serializers.DateTimeField()
    payload = serializers.DictField()
