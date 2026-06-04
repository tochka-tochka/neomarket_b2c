import logging
import requests
from celery import shared_task
from django.db import transaction
from src.models.orders import Order, FailedFulfillAttempts
from src.serializers.orders import OrderSerializer
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
        logging.info(f"Processed {len(orders)} orders.")
                
    return f"Processed {len(orders)} orders."

@shared_task(name="tasks.retry_fulfill_orders")
def retry_fulfill_orders():
    BATCH_SIZE = 100 
    
    with transaction.atomic():
        fulfill_attempt = (
            FailedFulfillAttempts.objects.all()[:BATCH_SIZE]
        )
        
        if not fulfill_attempt:
            return "No pending fulfill attempts orders found."

        for attempt in fulfill_attempt:
            b2b_client.fulfill_order(attempt.payload)
            attempt.delete()
        logging.info(f"Processed {len(fulfill_attempt)} orders.")
                
    return f"Processed {len(fulfill_attempt)} orders."