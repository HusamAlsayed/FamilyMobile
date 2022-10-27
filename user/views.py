from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from .serializers import UserSerializer
from .models import CustomUser
import jwt
import datetime
from user.services.authentication import get_token
from django.http import JsonResponse, HttpResponseForbidden
from django.forms.models import model_to_dict
from materials.models import Outlay
from django.views.decorators.csrf import csrf_exempt


class LoginView(APIView):
    def post(self, request):
        username = request.data['username']
        password = request.data['password']

        user = CustomUser.objects.filter(username=username).first()

        if user is None:
            raise AuthenticationFailed('User not found!')

        if not user.check_password(password):
            raise AuthenticationFailed('Incorrect password!')

        payload = {
            'id': user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
            'iat': datetime.datetime.utcnow()
        }
        token = jwt.encode(payload, 'secret', algorithm='HS256')

        response = Response()

        response.set_cookie(key='token', value=token, httponly=True)
        response.data = {
            'token': token,
            'user': model_to_dict(user)
        }
        return response


class UserView(APIView):
    def get(self, request):
        try:
            payload = get_token(request)
        except Exception:
            return AuthenticationFailed({"message": "Authentication Failed"})
        user = CustomUser.objects.filter(id=payload['id']).first()
        user_serializer = UserSerializer(user)
        return Response(user_serializer.data)


class SignUp(APIView):
    def post(self, request):
        username = request.data['username']
        password = request.data['password']
        token = get_token(request)
        parent_id = None if not token else token['id']
        user = CustomUser.objects.create_user(username=username,
                                              password=password,
                                              parent_user_id=parent_id)
        payload = {
            'id': user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
            'iat': datetime.datetime.utcnow()
        }
        token = jwt.encode(payload, 'secret', algorithm='HS256')
        return JsonResponse({"user": model_to_dict(user), "token": token})


class ChildSignUp(APIView):
    def post(self, request):
        token = get_token(request)
        if not token:
            return HttpResponseForbidden()
        parent_user_id = token['id']
        username = request.data['username']
        password = request.data['password']
        child_user = CustomUser.objects.create_user(username=username,
                                              password=password,
                                              parent_user_id=parent_user_id)
        payload = {
            'id': child_user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
            'iat': datetime.datetime.utcnow()
        }
        token = jwt.encode(payload, 'secret', algorithm='HS256')
        return JsonResponse({"user": model_to_dict(child_user), "token": token})


# @csrf_exempt
# def user_login(request):
#     if request.method != "POST":
#         return HttpResponse("Method not Allowed", status=405)
#     username = request.POST['username']
#     password = request.POST['password']
#     user = authenticate(request, username=username, password=password)
#     if user is not None:
#         login(request, user)
#         # user.
#         return HttpResponse("Login Successfully.")
#     else:
#         return HttpResponse("Password or Username are wrong", status=401)
#
#
# def user_logout(request):
#     logout(request)
#     return HttpResponse("Logout Successfully.")
