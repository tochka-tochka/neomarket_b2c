from src.services.catalog.products import get_product_card
from src.models.cart import CartItem
from django.conf import settings as django_settings

def check_service_key(request):
    key = request.headers.get('X-Service-Key')
    if not key:
        return False
    return key == django_settings.B2B_SERVICE_KEY


REASON_MAP = {
    'PRODUCT_BLOCKED': 'PRODUCT_BLOCKED',
    'PRODUCT_HARD_BLOCKED': 'PRODUCT_BLOCKED',
    'PRODUCT_DELETED': 'PRODUCT_DELETED',
    'SKU_OUT_OF_STOCK': 'OUT_OF_STOCK',
}


def handle_event(data):
    event_type = data['event_type']
    payload = data['payload']

    if event_type in ('PRODUCT_BLOCKED', 'PRODUCT_HARD_BLOCKED', 'PRODUCT_DELETED'):
        product_id = payload['product_id']
        response = get_product_card(product_id)

        if response.status_code != 200:
            return

        sku_ids = [sku['id'] for sku in response.json()['skus']]
        reason = REASON_MAP[event_type]

        CartItem.objects.filter(sku_id__in=sku_ids).update(unavailable_reason=reason)

    elif event_type == 'SKU_OUT_OF_STOCK':
        sku_id = payload['sku_id']
        reason = REASON_MAP[event_type]

        CartItem.objects.filter(sku_id=sku_id).update(unavailable_reason=reason)

    elif event_type in ('SKU_BACK_IN_STOCK', 'PRICE_CHANGED'):
        pass
