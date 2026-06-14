from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from src.services.events.events import check_service_key, handle_event
from src.models.events import ProcessedEvent
from src.serializers.events import B2BEventSerializer


class B2BEventsView(APIView):

    def post(self, request):
        if not check_service_key(request):
            return Response(
                {"code": "AUTHORIZATION_ERROR", "message": "X-Service-Key required."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        serializer = B2BEventSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"code": "VALIDATION_ERROR", "message": f"Invalid request data: {serializer.errors}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        data = serializer.validated_data
        idempotency_key = data['idempotency_key']

        if ProcessedEvent.objects.filter(idempotency_key=idempotency_key).exists():
            return Response(
                {"code": "REPEATED_IDEMPOTENCY_KEY", "message": "This idempotency key was already used."},
                status=status.HTTP_409_CONFLICT
            )

        handle_event(data)
        ProcessedEvent.objects.create(idempotency_key=idempotency_key)
        return Response(
            {"code": "ACCEPTED", "message": "Event was accepted."},
            status=status.HTTP_202_ACCEPTED
        )
