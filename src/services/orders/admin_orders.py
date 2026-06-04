from src.models import OrderOperations
from src.models.orders import Order, OperationTypes
from src.services.orders.orders import OrderNotFound
from interservice_connection.b2b_http_client.main import b2b_client

def fulfill_order(id):

    from src.serializers.orders import OrderSerializer
    
    try:
        existing = OrderOperations.objects.filter(order_id=id, type=OperationTypes.FULFILL).first()
        if existing is not None:
            return
        
        order = Order.objects.filter(id=id).first()
        if order is None:
            raise OrderNotFound()

        b2b_client.fulfill_order(OrderSerializer(order).data)

        OrderOperations.objects.create(
            order_id=id,
            type=OperationTypes.FULFILL
        )
    except OrderNotFound as e:
        raise e
    except Exception as e:
        raise e