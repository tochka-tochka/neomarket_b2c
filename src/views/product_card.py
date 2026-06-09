from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from src.services.catalog.products import get_product_card
from src.serializers.products import ProductCardSerializer


class ProductCardView(APIView):

    def get(self, request, id):

        try:
            response = get_product_card(id)
        except Exception as e:
            return Response(
                {"code": "SERVICE_UNAVAILABLE", "message": "Catalog temporarily unavailable"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        if response.status_code == 404:
            return Response(
                {"code": "NOT_FOUND", "message": "Product not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        b2b_data = response.json()

        for sku in b2b_data.get('skus', []):
            if sku.get('discount', 0) > 0:
                sku['old_price'] = sku['price']
                sku['price'] = sku['price'] - sku['discount']

            else:
                sku['old_price'] = None

            if 'active_quantity' in sku:
                sku['available_quantity'] = sku.pop('active_quantity')

        serializer = ProductCardSerializer(data=b2b_data)

        if not serializer.is_valid():
            print(f"Validation error for product {id}: {serializer.errors}")
            return Response(
                {"code": "INVALID_DATA", "message": "Invalid product data from catalog"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response(serializer.validated_data, status=status.HTTP_200_OK)