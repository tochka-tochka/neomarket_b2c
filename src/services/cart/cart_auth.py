from rest_framework_simplejwt.tokens import AccessToken
from src.errors import NeomarketRequestError

def get_user_id_from_jwt(request):
    auth_header = request.headers.get('Authorization')

    if not auth_header or not auth_header.startswith('Bearer '):
        return None

    token = auth_header.split(' ')[1]

    try:
        access_token = AccessToken(token)

        print(access_token)

        user_id = access_token.get('sub') or access_token.get('user_id')
        return user_id
    except Exception:
        return None


def get_session_id(request):
    return request.headers.get('X-Session-Id')


def get_cart_identity(request):
    user_id = get_user_id_from_jwt(request)

    if user_id:
        return ('user', user_id)

    session_id = get_session_id(request)
    if session_id:
        return ('session', session_id)

    raise NeomarketRequestError("Provide JWT (Bearer) or X-Session-Id header", "MISSING_CART_IDENTITY")


def get_cart_item_queryset(request, model):
    identity_type, identity_value = get_cart_identity(request)

    if identity_type == 'user':
        return model.objects.filter(user_id=identity_value)
    else:
        return model.objects.filter(session_id=identity_value)


def get_cart_item_or_404(request, model, item_id):
    identity_type, identity_value = get_cart_identity(request)

    try:
        if identity_type == 'user':
            return model.objects.get(sku_id=item_id, user_id=identity_value)
        else:
            return model.objects.get(sku_id=item_id, session_id=identity_value)
    except model.DoesNotExist:
        raise NeomarketRequestError("Cart item not found", "CART_ITEM_NOT_FOUND")