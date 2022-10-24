from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
import jwt


def get_token(request):
    print(request.META)
    token = request.headers.get('token')
    print(f'the token is {token}')
    if not token:
        return False
    try:
        payload = jwt.decode(token, 'secret', algorithms=['HS256'])
    except Exception:
        return False
    return payload
