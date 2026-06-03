from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.db import transaction

from src.models.cart import CartItem
from src.serializers.cart import CartResponseSerializer, CartItemCreateSerializer, CartItemUpdateSerializer
from src.services.cart.cart_auth import get_cart_identity, get_cart_item_or_404, get_session_id, get_user_id_from_jwt
from src.services.cart.enrich import get_skus_batch, get_sku_by_id


class CartView(APIView):

    def get(self, request):

        identity_type, identity_value = get_cart_identity(request)

        response_data = get_cart_response(identity_type, identity_value)

        serializer = CartResponseSerializer(data=response_data)

        if not serializer.is_valid():
            return Response(
                {"code": "VALIDATION_ERROR", "message": f"Invalid cart data: {serializer.errors}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(serializer.data)

    def delete(self, request):

        identity_type, identity_value = get_cart_identity(request)
        filter_kwargs = {f"{identity_type}_id": identity_value}
        CartItem.objects.filter(**filter_kwargs).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CartItemView(APIView):

    def post(self, request):

        identity_type, identity_value = get_cart_identity(request)

        serializer = CartItemCreateSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {"code": "VALIDATION_ERROR", "message": f"Invalid cart item data: {serializer.errors}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        sku_id = serializer.validated_data['sku_id']
        quantity = serializer.validated_data['quantity']

        sku_data = get_sku_by_id(str(sku_id))
        if sku_data is None:
            return Response(
                {"code": "SKU_NOT_FOUND", "message": "SKU does not exist"},
                status=status.HTTP_404_NOT_FOUND
            )

        active_quantity = sku_data.get('active_quantity', 0)
        if active_quantity < quantity:
            return Response(
                {"code": "INSUFFICIENT_STOCK", "message": f"Only {active_quantity} available"},
                status=status.HTTP_409_CONFLICT
            )

        with transaction.atomic():
            cart_item, created = CartItem.objects.select_for_update().get_or_create(
                **{f"{identity_type}_id": identity_value},
                sku_id=sku_id,
                defaults={'quantity': quantity}
            )

            if not created:
                cart_item.quantity += quantity
                cart_item.save()

        response_data = get_cart_response(identity_type, identity_value)

        status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        return Response(response_data, status=status_code)

    def patch(self, request, sku_id):

        identity_type, identity_value = get_cart_identity(request)

        serializer = CartItemUpdateSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {"code": "VALIDATION_ERROR", "message": f"Invalid cart item data: {serializer.errors}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        new_quantity = serializer.validated_data['quantity']

        cart_item = get_cart_item_or_404(request, CartItem, sku_id)

        sku_data = get_sku_by_id(str(cart_item.sku_id))
        if sku_data is None:
            return Response(
                {"code": "SKU_NOT_FOUND", "message": "SKU no longer exists"},
                status=status.HTTP_400_BAD_REQUEST
            )

        active_quantity = sku_data.get('active_quantity', 0)
        if active_quantity < new_quantity:
            return Response(
                {"code": "INSUFFICIENT_STOCK", "message": f"Only {active_quantity} available"},
                status=status.HTTP_409_CONFLICT
            )

        cart_item.quantity = new_quantity
        cart_item.save()

        response_data = get_cart_response(identity_type, identity_value)
        return Response(response_data, status=status.HTTP_200_OK)

    def delete(self, request, sku_id):

        identity_type, identity_value = get_cart_identity(request)
        cart_item = get_cart_item_or_404(request, CartItem, sku_id)

        cart_item.delete()

        response_data = get_cart_response(identity_type, identity_value)
        return Response(response_data, status=status.HTTP_200_OK)


class CartValidateView(APIView):

    def get(self, request):

        identity_type, identity_value = get_cart_identity(request)

        cart_data = get_cart_response(identity_type, identity_value)

        filter_kwargs = {f"{identity_type}_id": identity_value}
        cart_items = CartItem.objects.filter(**filter_kwargs)

        if not cart_items.exists():
            return Response({
                'is_valid': False,
                'cart': cart_data,
                'issues': []
            }, status=status.HTTP_200_OK)

        sku_ids = [str(item.sku_id) for item in cart_items]
        skus_data = get_skus_batch(sku_ids)

        issues = []
        is_valid = True

        for item in cart_items:
            sku_id = str(item.sku_id)
            sku_data = skus_data.get(sku_id)

            if sku_data is None:
                issues.append({
                    'sku_id': sku_id,
                    'type': 'PRODUCT_DELETED',
                    'message': 'Товар удалён или заблокирован'
                })
                is_valid = False
                continue

            active_quantity = sku_data.get('active_quantity', 0)
            if active_quantity == 0:
                issues.append({
                    'sku_id': sku_id,
                    'type': 'OUT_OF_STOCK',
                    'message': 'Товар отсутствует на складе'
                })
                is_valid = False
                continue

            if active_quantity < item.quantity:
                issues.append({
                    'sku_id': sku_id,
                    'type': 'QUANTITY_REDUCED',
                    'message': f'Доступно только {active_quantity} шт.',
                    'old_value': item.quantity,
                    'new_value': active_quantity
                })
                is_valid = False
                continue

            product_status = sku_data.get('status')
            if product_status in ('BLOCKED', 'HARD_BLOCKED'):
                issues.append({
                    'sku_id': sku_id,
                    'type': 'PRODUCT_BLOCKED',
                    'message': 'Товар заблокирован модерацией'
                })
                is_valid = False
                continue

        return Response({
            'is_valid': is_valid,
            'cart': cart_data,
            'issues': issues
        }, status=status.HTTP_200_OK)


class CartMergeView(APIView):

    def post(self, request):

        user_id = get_user_id_from_jwt(request)
        if not user_id:
            return Response(
                {"code": "UNAUTHORIZED", "message": "Valid JWT required"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        session_id = get_session_id(request)

        guest_items = CartItem.objects.filter(session_id=session_id, user_id__isnull=True)

        with transaction.atomic():
            for guest_item in guest_items:
                user_item = CartItem.objects.filter(
                    user_id=user_id,
                    sku_id=guest_item.sku_id,
                    session_id__isnull=True
                ).first()

                if user_item:
                    new_quantity = max(user_item.quantity, guest_item.quantity)
                    user_item.quantity = new_quantity
                    user_item.save()
                    guest_item.delete()
                else:
                    guest_item.user_id = user_id
                    guest_item.session_id = None
                    guest_item.save()

            CartItem.objects.filter(session_id=session_id, user_id__isnull=True).delete()

        cart_data = get_cart_response('user', user_id)

        return Response(cart_data, status=status.HTTP_200_OK)


def get_cart_response(identity_type, identity_value):

    filter_kwargs = {f"{identity_type}_id": identity_value}

    print(filter_kwargs)

    cart_items = CartItem.objects.filter(**filter_kwargs)

    if not cart_items.exists():
        response_data = {
            'id': identity_value,
            'items': [],
            'items_count': 0,
            'subtotal': 0,
            'is_valid': False,
            'updated_at': timezone.now()
        }

    else:
        sku_ids = [str(item.sku_id) for item in cart_items]
        skus_data = get_skus_batch(sku_ids)

        enriched_items = []
        items_count = 0
        subtotal = 0
        is_valid = True

        for item in cart_items:
            sku_id = str(item.sku_id)
            sku_data = skus_data.get(sku_id)

            if sku_data is None:
                enriched_items.append({
                    'sku_id': sku_id,
                    'product_id': None,
                    'name': 'Товар недоступен',
                    'quantity': item.quantity,
                    'unit_price': 0,
                    'line_total': 0,
                    'available_quantity': 0,
                    'is_available': False,
                    'sku_code': None,
                    'unit_price_at_add': None,
                    'image': None
                })
                items_count += item.quantity
                is_valid = False
                continue

            active_quantity = sku_data.get('active_quantity', 0)
            available = active_quantity >= item.quantity
            final_price = sku_data.get('price', 0) - sku_data.get('discount', 0)
            line_total = final_price * item.quantity if available else 0

            enriched_items.append({
                'sku_id': sku_id,
                'product_id': sku_data.get('product_id'),
                'name': sku_data.get('name'),
                'quantity': item.quantity,
                'unit_price': final_price,
                'line_total': line_total,
                'available_quantity': active_quantity,
                'is_available': available,
                'sku_code': sku_data.get('article'),
                'unit_price_at_add': None,
                'image': sku_data.get('images', [None])[0] if sku_data.get('images') else None
            })

            items_count += item.quantity
            subtotal += line_total
            if not available:
                is_valid = False

        response_data = {
            'id': identity_value,
            'items': enriched_items,
            'items_count': items_count,
            'subtotal': subtotal,
            'is_valid': is_valid and items_count > 0,
            'updated_at': timezone.now()
        }

    return response_data
