from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from src.models.favorite import Favorite
from src.serializers.favorite import PaginatedCatalogProductsSerializer
from src.services.cart.cart_auth import get_user_id_from_jwt
from src.services.favorite.enrich import get_products_batch


class FavoritesView(APIView):

    def get(self, request):
        user_id = get_user_id_from_jwt(request)
        
        if not user_id:
            return Response(
                {"code": "UNAUTHORIZED", "message": "Valid JWT required"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        limit = int(request.query_params.get('limit', 20))
        offset = int(request.query_params.get('offset', 0))

        favorites = Favorite.objects.filter(user_id=user_id)
        total_count = favorites.count()
        page = favorites.order_by('added_at')[offset:offset + limit]

        product_ids = [str(fav.product_id) for fav in page]
        products_batch = get_products_batch(product_ids)

        items = [products_batch[product_id] for product_id in product_ids if product_id in products_batch]

        response_data = {
            'items': items,
            'total_count': total_count,
            'limit': limit,
            'offset': offset,
        }

        serializer = PaginatedCatalogProductsSerializer(data=response_data)
        if not serializer.is_valid():
            return Response(
                {"code": "VALIDATION_ERROR", "message": f"Invalid response data: {serializer.errors}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(serializer.data, status=status.HTTP_200_OK)


class FavoriteDetailView(APIView):

    def put(self, request, product_id):
        user_id = get_user_id_from_jwt(request)

        if not user_id:
            return Response(
                {"code": "UNAUTHORIZED", "message": "Valid JWT required"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        products_map = get_products_batch([str(product_id)])
        if str(product_id) not in products_map:
            return Response(
                {"code": "PRODUCT_NOT_FOUND", "message": "Product does not exist or is unavailable"},
                status=status.HTTP_404_NOT_FOUND
            )

        Favorite.objects.get_or_create(user_id=user_id, product_id=product_id)

        return Response(status=status.HTTP_204_NO_CONTENT)

    def delete(self, request, product_id):
        user_id = get_user_id_from_jwt(request)

        if not user_id:
            return Response(
                {"code": "UNAUTHORIZED", "message": "Valid JWT required"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        Favorite.objects.filter(user_id=user_id, product_id=product_id).delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
