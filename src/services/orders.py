import requests
from django.db import transaction

from interservice_connection.b2b_http_client.main import b2b_client
from src.models.orders import Order, OrderItem, OrderOperations
from src.serializers.orders import OrderSerializer

class AccessDenied(Exception):
    pass

class OrderNotFound(Exception):
    pass

class BadRequestException(Exception):
    pass

class CancelNotAllowed(Exception):
    def __init__(self, message, current_status):
        super().__init__(message)
        self.current_status = current_status


class ConflictError(Exception):
    def __init__(self, message, conflicts):
        super().__init__(message)
        self.conflicts = conflicts


def find_sku(products, sku_id):
    for product in products:
        for sku in product["skus"]:
            if sku["id"] == sku_id:
                return sku | {"product": product}


@transaction.atomic
def create_order(user, idempotency_key, data):
    try:
        existing = OrderOperations.objects.filter(
            idempotency_key=idempotency_key
        ).first()
        if existing:
            return OrderSerializer(existing.order).data

        if not idempotency_key:
            raise BadRequestException("idempotency_key is required")

        if data["items"] is None or len(data["items"]) == 0:
            raise BadRequestException("items can't be empty")

        ids = [item["sku_id"] for item in data["items"]]
        products = b2b_client.get_products_by_sku_ids(ids).json()

        failed = []
        for item in data["items"]:
            sku = find_sku(products, item["sku_id"])
            if not sku:
                failed.append({"sku_id": item["sku_id"], "reason": "SKU_NOT_FOUND"})
            elif sku["product"]["status"] == "BLOCKED":
                failed.append({"sku_id": item["sku_id"], "reason": "PRODUCT_BLOCKED"})
            elif sku["product"]["deleted"]:
                failed.append({"sku_id": item["sku_id"], "reason": "PRODUCT_DELETED"})
            elif sku["reserved_quantity"] < item["quantity"]:
                failed.append({"sku_id": item["sku_id"], "reason": "RESERVE_FAILED"})

        if failed:
            raise ConflictError("failed to reserve items", failed)

        order = Order.objects.create(
            buyer=user,
            number="ORD-SKU",
            status="PAID",
            address_id=data["address_id"],
        )

        for item in data["items"]:
            sku = find_sku(products, item["sku_id"])
            OrderItem.objects.create(
                order=order,
                sku_id=item["sku_id"],
                product_id=sku["product"]["id"],
                name=sku["name"],
                quantity=item["quantity"],
                unit_price=sku["price"],
                line_total=item["quantity"] * sku["price"],
                image_url=sku["images"][0]["url"] or "",
            )

        OrderOperations.objects.create(
            idempotency_key = idempotency_key,
            order = order
        )
        return OrderSerializer(order).data
    except BadRequestException as e:
        raise e
    except requests.ConnectionError as e:
        raise e
    except ConflictError as e:
        raise e
    except Exception as e:
        raise Exception(f"failed to create order: {str(e)}")

@transaction.atomic
def cancel_order(user, order_id):
    try:
        order = Order.objects.filter(id=order_id, buyer=user).first()
    
        if order is None:
            raise OrderNotFound("order not found")

        if order.status != "CREATED" and order.status != "PAID":
            raise CancelNotAllowed("cancel not allowed", order.status)

        try:
            b2b_client.unreserve_skus(OrderSerializer(order).data)
    
            order.status = "CANCELED"
        except requests.ConnectionError as e:
            order.status = "CANCEL_PENDING"

        order.save()

        return OrderSerializer(order).data
    except OrderNotFound as e:
        raise e
    except CancelNotAllowed as e:
        raise e
        