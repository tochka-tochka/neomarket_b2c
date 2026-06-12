from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import IntegrityError, transaction

from src.models.subscriptions import ProductSubscription
from src.services.cart.cart_auth import get_user_id_from_jwt
from src.services.catalog.products import get_product_card

VALID_EVENTS = {'BACK_IN_STOCK', 'PRICE_DROP'}


class ProductSubscriptionView(APIView):

    def post(self, request, product_id):
        user_id = get_user_id_from_jwt(request)

        if not user_id:
            return Response(
                {"code": "UNAUTHORIZED", "message": "Valid JWT required"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        events = request.data.get('events', list(VALID_EVENTS))

        if not events or not isinstance(events, list):
            return Response(
                {"code": "INVALID_NOTIFY_ON", "message": "events must be a non-empty list"},
                status=status.HTTP_400_BAD_REQUEST
            )

        invalid = [event for event in events if event not in VALID_EVENTS]
        if invalid:
            return Response(
                {"code": "INVALID_NOTIFY_ON", "message": f"Invalid events: {invalid}. Allowed: {VALID_EVENTS}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        product_response = get_product_card(product_id)
        if product_response.status_code == 404:
            return Response(
                {"code": "PRODUCT_NOT_FOUND", "message": "Product does not exist or is unavailable"},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            with transaction.atomic():
                ProductSubscription.objects.create(
                    user_id=user_id,
                    product_id=product_id,
                    events=events,
                )
        except IntegrityError:
            return Response(
                {"code": "SUBSCRIPTION_ALREADY_EXISTS", "message": "Already subscribed to this product"},
                status=status.HTTP_409_CONFLICT
            )

        return Response(status=status.HTTP_204_NO_CONTENT)

    def delete(self, request, product_id):
        user_id = get_user_id_from_jwt(request)

        if not user_id:
            return Response(
                {"code": "UNAUTHORIZED", "message": "Valid JWT required"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        ProductSubscription.objects.filter(user_id=user_id, product_id=product_id).delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
