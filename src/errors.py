from django.http import JsonResponse
from rest_framework.exceptions import APIException
from rest_framework.views import exception_handler


class NeomarketServiceError(APIException):
    status_code = 503


class NeomarketRequestError(APIException):
    status_code = 400


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if not isinstance(exc, APIException):
        if response is not None:
            response.data['status_code'] = response.status_code
        return response

    return JsonResponse(
        exc.get_full_details(),
        status=exc.status_code,
        safe=False
    )
