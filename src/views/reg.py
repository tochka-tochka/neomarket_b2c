from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from src.serializers.reg import RegisterSerializer


@method_decorator(csrf_exempt, name="dispatch")
class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            seller = serializer.save()

            refresh = RefreshToken.for_user(seller)
            return Response(
                {
                    "seller": serializer.data,
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
                status=status.HTTP_201_CREATED,
                headers={
                    "Set-Cookie": f"refresh={refresh}; HttpOnly; Path=/",
                },
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
