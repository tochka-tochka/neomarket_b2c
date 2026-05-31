import requests
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from src.services.orders.orders import (
    BadRequestException,
    CancelNotAllowed,
    ConflictError,
    InvalidPaginationParam,
    OrderNotFound,
    ReserveFailed,
    create_order,
    cancel_order,
    get_order_by_id,
    get_orders,
)


@method_decorator(csrf_exempt, name="dispatch")
class OrdersView(APIView):
    access_classes = [IsAuthenticated]
    parser_classes = [JSONParser]

    def post(self, request):
        try:
            data = {
                "address_id": request.data.get("address_id"),
                "payment_method_id": request.data.get("payment_method_id"),
                "comment": request.data.get("comment"),
                "items": request.data.get("items_snapshot"),
            }
            order = create_order(
                request.user, request.headers.get("Idempotency-Key"), data
            )
            return JsonResponse(order, status=201)
        except BadRequestException as e:
            return JsonResponse(
                {
                    "code": "INVALID_REQUEST",
                    "message": str(e),
                },
                status=400
            )
        except requests.ConnectionError:
            return JsonResponse(
                {
                    "code": "B2B_UNAVAILABLE",
                    "message": "Service is unavailable right now",
                },
                status=503,
            )
        except ConflictError as e:
            return JsonResponse(
                {
                    "code": "RESERVE_FAILED",
                    "message": str(e),
                    "failed_items": e.conflicts,
                },
                status=409,
            )
        except ReserveFailed as e:
            return JsonResponse(str(e), status=409)
        except Exception as e:
            return JsonResponse({"code": "SERVER_ERROR", "msg": str(e)}, status=500)

    def get(self, request):
        try:
            orders, count, limit, offset = get_orders(
                request.user,
                request.query_params.get("status"),
                request.query_params.get("limit"),
                request.query_params.get("offset"),
            )

            return JsonResponse(
                {"items": orders, "count": count, "limit": limit, "offset": offset},
                status=200,
            )
        except OrderNotFound:
            return JsonResponse({"code": "NOT_FOUND", "message": "Order not found"})
        except InvalidPaginationParam as e:
            return JsonResponse({"code": "INVALID_REQUEST", "message": str(e)})
        except Exception:
            return JsonResponse({"code": "SERVER_ERROR"}, status=500)


@method_decorator(csrf_exempt, name="dispatch")
class OrdersDetailView(APIView):
    access_classes = [IsAuthenticated]
    parser_classes = [JSONParser]

    def get(self, request, id):
        try:
            order = get_order_by_id(request.user, id)
            return JsonResponse(order, status=200)
        except OrderNotFound:
            return JsonResponse({"code": "NOT_FOUND", "message": "Order not found"}, status=404)
        except Exception:
            return JsonResponse({"code": "SERVER_ERROR"}, status=500)

@method_decorator(csrf_exempt, name="dispatch")
class OrderDeleteView(APIView):
    access_classes = [IsAuthenticated]
    parser_classes = [JSONParser]

    def post(self, request, id):
        try:
            canceled_order = cancel_order(request.user, id)
            return JsonResponse(canceled_order, status=200)
        except OrderNotFound:
            return JsonResponse(
                {"code": "ORDER_NOT_FOUND", "message": "order not found"}, status=404
            )
        except CancelNotAllowed as e:
            return JsonResponse(
                {
                    "code": "CANCEL_NOT_ALLOWED",
                    "message": str(e),
                    "current_status": e.current_status,
                },
                status=409,
            )
        except Exception:
            return JsonResponse({"code": "SERVER_ERROR"}, status=500)
