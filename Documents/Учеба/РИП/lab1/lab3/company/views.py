from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import status
from company.serializers import *
from company.models import *
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser
from rest_framework.parsers import MultiPartParser, FormParser
from company.stocks.minio import add_pic, del_pic
import datetime

# Create your views here.

def user():
    try:
        user1 = AuthUser.objects.get(id=2)
    except:
        user1 = AuthUser(id=2, first_name="Иван", last_name="Иванов", password=1234, username="user1")
        user1.save()
    return user1

@api_view(["GET", "POST"])
def personalities_catalog(request):
    if request.method == 'GET':
        personalities = Personalities.objects.all()
        serializer = PersonalitiesSerializer(personalities, many=True)
        printed_count = None
        selected_company_id = None
        selected_user = user()
        selected_company = Company.objects.filter(status=1, user=selected_user.id)
        if selected_company.count() != 0:
            selected_company_id = selected_company[0].id
            printed_count = CompanyUser.objects.filter(company=selected_company_id).count()
        response = {
            "personalities": serializer.data,
            "company_id": selected_company_id,
            "company_count": printed_count
        }
        return Response(response, status=status.HTTP_200_OK)
    elif request.method == 'POST':
        parsed_data = JSONParser().parse(request)
        serializer = PersonalitiesSerializer(data=parsed_data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK) 
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "PUT", "DELETE", "POST"])
def personality_card(request, id):
    try: 
        personality = Personalities.objects.get(id=id) 
    except Personalities.DoesNotExist: 
        return Response({"message": "Person not found"}, status=status.HTTP_400_BAD_REQUEST)
    if request.method == 'GET':
        serializer = PersonalitiesSerializer(personality)
        response = serializer.data
        return Response(response, status=status.HTTP_200_OK)
    elif request.method == 'PUT':
        parsed_data = JSONParser().parse(request)
        if 'pic' in parsed_data:
            pic_result = add_pic(personality, parsed_data.initial_data['pic'])
            if 'error' in pic_result.data:
                return Response({"message": pic_result}, status=status.HTTP_400_BAD_REQUEST)
        serializer = PersonalitiesSerializer(personality, data=parsed_data, partial=True) 
        if serializer.is_valid(): 
            serializer.save() 
            return Response(serializer.data, status=status.HTTP_200_OK) 
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 
    elif request.method == 'DELETE':
        pic_result = del_pic(personality)
        if 'error' in pic_result:
            return Response({"message": pic_result}, status=status.HTTP_400_BAD_REQUEST)
        personality.delete() 
        return Response({"message": "Person was deleted successfully!"}, status=status.HTTP_200_OK)
    elif request.method == 'POST':
        # Используем MultiPartParser для обработки файлов
        pic_file = request.FILES['pic']
        # Проверяем наличие файла в parsed_data
        if pic_file != None:
            pic_result = add_pic(personality, pic_file)
            if 'error' in pic_result:
                return Response({"message": pic_result}, status=status.HTTP_400_BAD_REQUEST)
            personality.image = pic_result["message"]
            personality.save()
            serializer = PersonalitiesSerializer(Personalities.objects.get(id=id) ) 
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"message": "not a image"}, status=status.HTTP_400_BAD_REQUEST) 
    

@api_view(["GET", "POST"])
def companies(request):
    if request.method == 'GET':
        companies =  Company.objects.filter(status__gte = 3).order_by('created_date', 'status')
        if companies.count() == 0:
            companies = None
        serializer = CompanySerializer(companies, many=True)
        response = serializer.data
        return Response(response, status=status.HTTP_200_OK)
    elif request.method == 'POST':
        parsed_data = JSONParser().parse(request)
        serializer = CompanySerializer(data=parsed_data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK) 
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "PUT", "DELETE"])
def company(request, id):
    try: 
        company = Company.objects.get(id=id) 
    except Company.DoesNotExist: 
        return Response(None, status=status.HTTP_200_OK)
    if request.method == 'GET':
        serializer = CartSerializer(company)
        response = serializer.data
        return Response(response, status=status.HTTP_200_OK)
    elif request.method == 'PUT':
        parsed_data = JSONParser().parse(request)
        serializer = EditCartSerializer(company, data=parsed_data, partial=True) 
        if serializer.is_valid(): 
            serializer.save() 
            return Response(serializer.data) 
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 
    elif request.method == 'DELETE':
        company.status = 2
        company.save() 
        return Response({"message": "Company was deleted successfully!"}, status=status.HTTP_200_OK)


@api_view(["POST"])
def add_item(request, id):
    selected_user = user()
    try: 
        company = Company.objects.get(user=selected_user, status=1) 
    except Company.DoesNotExist: 
        company = Company(user=selected_user, status=1)
        company.save()
    try:
        personality = Personalities.objects.get(id=id)
    except Personalities.DoesNotExist:
        return Response({"message": "Person with id={id} does not exist"}, status=status.HTTP_400_BAD_REQUEST)
    try: 
        item = CompanyUser.objects.get(company=company, user_id=personality) 
    except CompanyUser.DoesNotExist: 
        item = CompanyUser(company=company, user_id=personality, kol_akc=0)
    item.kol_akc += 1
    item.save()
    cart_items = CompanyUser.objects.filter(company=company)
    serializer = ItemsSerializer(cart_items, many=True)
    response = serializer.data
    return Response(response, status=status.HTTP_200_OK)


@api_view(["POST", "PUT"])
def user_registration(request):
    parsed_data = JSONParser().parse(request)
    if request.method == 'POST':
        serializer = UserSerializer(data=parsed_data)
        if serializer.is_valid():
            try:
                serializer.save()
            except:
                return Response({"message": "Used username"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message": "Not valid"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data, status=status.HTTP_200_OK)
    elif request.method == 'PUT':
        try:
            user = AuthUser.objects.get(username = parsed_data['username'], password = parsed_data['password'])
        except AuthUser.DoesNotExist:
            return Response({"message": "Cant login"}, status=status.HTTP_400_BAD_REQUEST)
        serializer = EditUserSerializer(user, data=parsed_data, partial=True)
        if serializer.is_valid():
            serializer.save()
        else:
            return Response({"message": "Bad data"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["POST"])
def user_auth(request):
    parsed_data = JSONParser().parse(request)
    try:
        user = AuthUser.objects.get(username = parsed_data['username'], password = parsed_data['password'])
    except AuthUser.DoesNotExist:
        return Response({"message": "Cant login"}, status=status.HTTP_400_BAD_REQUEST)
    return Response({"message": "login succesfuly"}, status=status.HTTP_200_OK)


@api_view(["POST"])
def user_deauth(request):
    parsed_data = JSONParser().parse(request)
    try:
        user = AuthUser.objects.get(username = parsed_data['username'], password = parsed_data['password'])
    except AuthUser.DoesNotExist:
        return Response({"message": "Cant logout"}, status=status.HTTP_400_BAD_REQUEST)
    return Response({"message": "logout succesfuly"}, status=status.HTTP_200_OK)


@api_view(["POST"])
def submit_company(request, id):
    try: 
        company = Company.objects.get(id=id, status=1) 
    except Company.DoesNotExist: 
        return Response(None, status=status.HTTP_200_OK)
    if company.company_name != None and company.description != None:
        company.status = 3
        company.submited_date = datetime.datetime.now()
        company.save()
        serializers = CartSerializer(company)
        return Response(serializers.data, status=status.HTTP_200_OK)
    return Response({"message": "Not valid"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(["POST"])
def accept_company(request, id):
    try: 
        company = Company.objects.get(id=id, status=3) 
    except Company.DoesNotExist: 
        return Response({"message": "Company not found"}, status=status.HTTP_200_OK)
    if company.company_name != None and company.description != None and company.submited_date != None:
        company.status = 4
        company.accepted_date = datetime.datetime.now()
        company.save()
        serializers = CartSerializer(company)
        return Response(serializers.data, status=status.HTTP_200_OK)
    return Response({"message": "Not valid"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["PUT", "DELETE"])
def company_user(request, id):
    try: 
        item = CompanyUser.objects.get(id=id) 
    except CompanyUser.DoesNotExist: 
        return Response({"message": "cant get item"}, status=status.HTTP_200_OK)
    if request.method == 'PUT':
        parsed_data = JSONParser().parse(request)
        serializer = ItemsSerializer(item, data=parsed_data, partial=True)
        if serializer.is_valid():
            serializer.save()
        else:
            return Response({"message": "Not valid"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data, status=status.HTTP_200_OK)
    elif request.method == 'DELETE':
        item.delete()
        return Response({"message": "Deleted succesfuly"}, status=status.HTTP_200_OK)