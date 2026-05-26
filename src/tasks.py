import logging
import requests
from celery import shared_task
from django.db import transaction
from .models import Order
from .serializers.orders import OrderSerializer
from interservice_connection.b2b_http_client.main import b2b_client

logger = logging.getLogger(__name__)

@shared_task(name="tasks.resend_failed_cancelled_orders")
def resend_failed_cancelled_orders():
    BATCH_SIZE = 100 
    
    with transaction.atomic():
        orders = (
            Order.objects.filter(status="CANCEL_PENDING")[:BATCH_SIZE]
        )
        
        if not orders:
            return "No pending cancelled orders found."

        for order in orders:
                try:
                    b2b_client.unreserve_skus(OrderSerializer(order).data)
                    order.status = "CANCELLED"
                    order.save()
                except requests.ConnectionError:
                    pass
                
    return f"Processed {len(orders)} orders."