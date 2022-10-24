from django.urls import path
from . import views

urlpatterns = [path('outlay', views.add_expense),
               path('outlay/<int:outlay_id>', views.change_expense),
               path('outlaytype', views.add_outlay_type),
               path('outlaytype/<int:outlaytype_id>', views.change_outlay_type),
               path('material', views.add_material),
               path('material/<int:material_id>', views.modify_material)]
