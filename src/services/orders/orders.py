import uuid

import requests
from django.db import transaction
from django.db.models import Q
from rest_framework import status

from interservice_connection.b2b_http_client.main import b2b_client
from src.models.orders import (
    OperationTypes,
    Order,
    OrderItem,
    OrderOperations,
    OrderStatus,
)
from src.models.cart import CartItem
from src.serializers.orders import OrderSerializer
from src.serializers.cart import CartItemSerializer


class AccessDenied(Exception):
    pass


class OrderNotFound(Exception):
    pass


class ReserveFailed(Exception):
    pass


class UnreserveFailed(Exception):
    pass


class BadRequestException(Exception):
    pass


class InvalidPaginationParam(Exception):
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
            idempotency_key=idempotency_key, type=OperationTypes.CREATE
        ).first()
        if existing:
            return OrderSerializer(existing.order).data

        if not idempotency_key:
            raise BadRequestException("idempotency_key is required")

        cart_items = CartItem.objects.filter(user_id = user.id)

        failed = []
        sku_ids = [str(item.sku_id) for item in cart_items]
        product_ids = []
        
        for id in sku_ids:
            response = b2b_client.get_sku(id)
            if response.status_code == status.HTTP_404_NOT_FOUND:
                failed.append({"sku_id": id, "reason": "SKU_NOT_FOUND"})
                continue
            sku = response.json()
            product_ids.append(sku["product_id"])

        products = b2b_client.get_products(product_ids).json()

        for item in cart_items:
            sku = find_sku(products, str(item.sku_id))
            product = sku["product"]
            
            if product["status"] != "MODERATED":
                failed.append({"sku_id": str(item.sku_id), "reason": "PRODUCT_NOT_MODERATED"})
            elif product["status"] == "BLOCKED":
                failed.append({"sku_id": str(item.sku_id), "reason": "PRODUCT_BLOCKED"})
            elif product["deleted"]:
                failed.append({"sku_id": str(item.sku_id), "reason": "PRODUCT_DELETED"})
            elif sku["active_quantity"] < item.quantity:
                failed.append({"sku_id": str(item.sku_id), "reason": "RESERVE_FAILED"})

        if len(failed) > 0:
            raise ConflictError("failed to validate items", failed)

        order_id = uuid.uuid4()
        
        response = b2b_client.reserve_skus(idempotency_key, order_id, cart_items)
        if response.status_code == status.HTTP_409_CONFLICT:
            raise ReserveFailed(response.json())

        order = Order.objects.create(
            id=order_id,
            buyer=user,
            number=f"ORD-{uuid.uuid4().hex[:8].upper()}",
            status="PAID",
            address_id=data["address_id"],
        )

        for item in cart_items:
            sku = find_sku(products, str(item.sku_id))
            preview_image = sku["images"][0] if sku.get("images") else ""
            
            OrderItem.objects.create(
                order=order,
                sku_id=str(item.sku_id),
                product_id=sku["product"]["id"],
                name=sku["name"],
                quantity=item.quantity,
                unit_price=sku["price"],
                line_total=item.quantity * sku["price"],
                image_url=preview_image,
            )

        OrderOperations.objects.create(
            idempotency_key=idempotency_key, order=order, type=OperationTypes.CREATE
        )

        return OrderSerializer(order).data

    except (BadRequestException, ConflictError, ReserveFailed, requests.ConnectionError) as e:
        raise e
    except Exception as e:
        raise Exception(f"failed to create order: {str(e)}")


@transaction.atomic
def cancel_order(user, order_id):
    try:
        existing = OrderOperations.objects.filter(
            order_id=order_id, type=OperationTypes.CANCEL
        ).first()
        if existing:
            return OrderSerializer(existing.order).data
        order = Order.objects.filter(id=order_id, buyer=user).first()

        if order is None:
            raise OrderNotFound("order not found")

        if (
            order.status != OrderStatus.CREATED
            and order.status != OrderStatus.PAID
            and order.status != OrderStatus.ASSEMBLING
        ):
            raise CancelNotAllowed("cancel not allowed", order.status)

        try:
            response = b2b_client.unreserve_skus(OrderSerializer(order).data)
            if response.status_code != status.HTTP_200_OK:
                order.status = OrderStatus.CANCEL_PENDING
            else:
                order.status = OrderStatus.CANCELLED
        except requests.ConnectionError:
            order.status = OrderStatus.CANCEL_PENDING

        order.save()

        OrderOperations.objects.create(
            idempotency_key=uuid.uuid4(), order=order, type=OperationTypes.CANCEL
        )
        return OrderSerializer(order).data
    except OrderNotFound as e:
        raise e
    except CancelNotAllowed as e:
        raise e


def get_orders(user, status, limit, offset):
    try:
        query = Q(buyer=user)

        if status is not None:
            query &= Q(status=status)

        try:
            limit = int(limit)
            if limit <= 0:
                raise InvalidPaginationParam("limit must be greater 0")
            if limit > 100:
                raise InvalidPaginationParam("limit must be less 100")
        except ValueError:
            raise InvalidPaginationParam("limit must be a number")

        if offset is None:
            offset = 0
        try:
            offset = int(offset)
            if offset < 0:
                raise InvalidPaginationParam("offset must be greater or equal 0")
        except ValueError:
            raise InvalidPaginationParam("offset must be a number")

        count = Order.objects.filter(query).count()

        orders = Order.objects.filter(query)[int(offset) : int(offset) + int(limit)]

        return OrderSerializer(orders, many=True).data, count, int(limit), int(offset)
    except Exception as e:
        raise e


def get_order_by_id(user, id):
    try:
        order = Order.objects.filter(buyer=user, id=id).first()
        if order is None:
            raise OrderNotFound()

        return OrderSerializer(order).data
    except OrderNotFound as e:
        raise e
    except Exception as e:
        raise e
