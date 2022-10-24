from django.shortcuts import render

# Create your views here.
from django.http import JsonResponse, HttpResponseNotFound, HttpResponseNotAllowed, \
    HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from .models import Outlay, Material, OutlayType
from django.forms.models import model_to_dict
import json
from django.core.exceptions import ObjectDoesNotExist
from user.services.authentication import get_token


@csrf_exempt
def add_expense(request):
    token = get_token(request)
    if not token:
        return HttpResponseForbidden()
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        data['user_id'] = token['id']
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
    data = json.loads(request.body.decode('utf-8'))
    material = Material.objects.create(**data)
    return JsonResponse({"material": model_to_dict(material)})


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
    token = get_token(request)
    print(f'the token is {token}')
    data = json.loads(request.body.decode('utf-8'))
    outlay_type = OutlayType.objects.create(**data)
    return JsonResponse({"material": model_to_dict(outlay_type)})

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
    year = request.GET.get('year', -1)
    month = request.GET.get('month', -1)
    if month != -1 and year != -1:
        expenses = Outlay.objects.filter(date__year=year, date__month=month)
    elif month != -1:
        expenses = Outlay.objects.filter(date__month=month)
    elif year != -1:
        expenses = Outlay.objects.filter(date__year=year)
    else:
        expenses = Outlay.objects.all()
    return JsonResponse({"expenses": list(expenses.values())})


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
