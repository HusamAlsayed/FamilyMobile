from django.urls import path
from django.urls import path
from .views import LoginView, UserView, SignUp
from . import views
urlpatterns = [path('login', LoginView.as_view()),
               path('signup', SignUp.as_view()),
               path('token', UserView.as_view())]
