from django.shortcuts import render

# Create your views here.
from django.http import JsonResponse, HttpResponseNotFound, HttpResponseNotAllowed, \
    HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from .models import Outlay, Material, OutlayType
from user.models import CustomUser
from django.forms.models import model_to_dict
import json
from django.core.exceptions import ObjectDoesNotExist
from user.services.authentication import get_token
from django.db.models import F

@csrf_exempt
def add_expense(request):
    token = get_token(request)
    print(f'the token is {token}')
    if not token:
        return HttpResponseForbidden()
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        data['user_id'] = token['id']
        data['price'] = int(data['price'])
        outlay = Outlay.objects.create(**data)
        return JsonResponse({"outlay": model_to_dict(outlay)})
    elif request.method == "GET":
        return get_date_expenses(request)


@csrf_exempt
def change_expense(request, outlay_id):
    outlay = Outlay.objects.get(pk=outlay_id)
    if not outlay:
        return HttpResponseNotFound()
    if request.method == "DELETE":
        outlay.delete()
        return JsonResponse({"message":"Deteled!"})
    elif request.method == "PUT":
        outlay.price = request.POST.get('price', outlay.price)
        outlay.description = request.POST.get('price', outlay.description)
        outlay.save()
        return JsonResponse({"message": "Updated successfully"})
    else:
        return HttpResponseNotAllowed({"Message":"Not allowed"})


@csrf_exempt
def add_material(request):
    token = get_token(request)
    if not token:
        return HttpResponseForbidden({"message": "You are not Authorized!"})
    token_user = CustomUser.objects.get(pk=token['id'])
    if request.method == "GET":
        values = token_user.material_set.all().values()
        return JsonResponse({"materials": list(values)})
        # return HttpResponseNotAllowed({"message": "only post method is allowed!"})
    elif request.method == "POST":
        user_id = token['id']
        user = CustomUser.objects.get(pk=user_id)
        print(f'the parent user is {user.parent_user}')
        if user.parent_user:
            return HttpResponseForbidden()
        data = json.loads(request.body.decode('utf-8'))
        data['user_id'] = user_id
        material = Material.objects.create(**data)
        return JsonResponse({"material": model_to_dict(material)})
    else:
        return HttpResponseNotAllowed({"message": "The method is not allowed!"})

@csrf_exempt
def modify_material(request, material_id):
    try:
        material = Material.objects.get(pk=material_id)
    except ObjectDoesNotExist:
        return HttpResponseNotFound()
    if request.method == "PUT":
        data = json.loads(request.body.decode('utf-8'))
        material.name = data.get('name', material.name)
        material.description = data.get('description', material.description)
        material.is_service = data.get('is_service', material.is_service)
        material.save()
        return JsonResponse({"Message": "Updated Successfully",
                             "data": model_to_dict(material)})
@csrf_exempt
def add_outlay_type(request):
    # token = get_token(request)
    # print(f'the token is {token}')
    if request.method == "GET":
        return JsonResponse({"outlayes": list(OutlayType.objects.all().values())})
    elif request.method == "POST":
        print(f'the body is {request.body.decode("utf-8")}')
        data = json.loads(request.body.decode('utf-8'))
        outlay_type = OutlayType.objects.create(**data)
        return JsonResponse({"outlay": model_to_dict(outlay_type)})
    else:
        return HttpResponseNotAllowed({"message": "The method is not allowed!"})



@csrf_exempt
def change_outlay_type(request, outlaytype_id: int):
    try:
        outlay_type = OutlayType.objects.get(pk=outlaytype_id)
    except ObjectDoesNotExist:
        return HttpResponseNotFound()
    data = json.loads(request.body.decode('utf-8'))
    outlay_type.name = data.get('name', outlay_type.name)
    outlay_type.description = data.get('name', outlay_type.description)
    outlay_type.save()
    return JsonResponse({"outlaytype": model_to_dict(outlay_type)})


def get_date_expenses(request):
    total_expenses = 0
    token = get_token(request)
    if not token:
        return HttpResponseForbidden()
    user_id = token['id']
    query_params = dict(request.GET)
    new_query_params = {}
    for key, value in query_params.items():
        if key == 'month' or key == 'year':
            new_query_params['date__' + key] = value[0]
            continue
        if key == 'is_service':
            new_query_params['material_id__is_service'] = value[0]
    token_user = CustomUser.objects.get(pk=user_id)
    if not token_user.parent_user:
        all_expenses = []
        child_users = token_user.customuser_set.all()
        for user in child_users:
            new_query_params['user_id'] = user.id
            expenses = Outlay.objects.filter(**new_query_params).\
                select_related('material').annotate(is_service=F('material__is_service')).\
                values()
            all_expenses.extend(expenses)
        new_query_params['user_id'] = user_id
        all_expenses.extend(Outlay.objects.filter(**new_query_params).select_related('material').
                            annotate(is_service=F('material__is_service')).values())
        for expense in all_expenses:
            total_expenses += expense['price']
        return JsonResponse({"expenses": all_expenses, "total_expense": total_expenses})
    # print(new_query_params)
    new_query_params['user_id'] = user_id

    expenses = Outlay.objects.filter(**new_query_params).\
        select_related('material').annotate(is_service=F('material__is_service'))
    for expense in expenses.values():
        total_expenses += expense['price']
    print(f'the expenses values is {expenses}')
    return JsonResponse({"expenses": list(expenses.values()),
                         "total_expense": total_expenses})


def get_expenses(request):
    token = get_token(request)
    if not token:
        return HttpResponseForbidden()
    user_id = token['id']
    service = request.params.get('service', -1)
    if service != 0:
        expenses = Outlay.objects.filter(user_id=user_id, is_service=service)
    else:
        expenses = Outlay.objects.filter(user_id=user_id)
    return JsonResponse({"expenses": list(expenses.values())})
