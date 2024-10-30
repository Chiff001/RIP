from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import status
from company.serializers import *
from company.models import *
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes, authentication_classes, parser_classes
from rest_framework.parsers import JSONParser
from rest_framework.parsers import MultiPartParser, FormParser
from company.stocks.minio import add_pic, del_pic
import datetime
from drf_yasg.utils import swagger_auto_schema
from company.permissions import *
from company.redis import session_storage
from django.contrib.auth import authenticate, login, logout
from rest_framework.permissions import *
from django.views.decorators.csrf import csrf_exempt
import uuid

# Create your views here.

def method_permission_classes(classes):
    def decorator(func):
        def decorated_func(self, *args, **kwargs):
            self.permission_classes = classes        
            self.check_permissions(self.request)
            return func(self, *args, **kwargs)
        return decorated_func
    return decorator

def get_user(request):
    session_id = request.COOKIES.get("session_id")
    print("Cookie_id", session_id)
    if session_id is None:
        return None
    else:
        username = session_storage.get(session_id).decode("utf-8")
        try:
            user = User.objects.get(username=username)
            print(user.username)
            return user
        except:
            print("cant get user")
            user = None
            return user


class personalities_catalog(APIView):
    @method_permission_classes([AllowAny])
    def get(self, request):
        try:
            parsed_data = JSONParser().parse(request)
            if parsed_data['peson_name'] != None:
                personalities = Personalities.objects.filter(name = parsed_data['peson_name'])
            else:
                personalities = Personalities.objects.all()
        except:
            personalities = Personalities.objects.all()
        serializer = PersonalitiesSerializer(personalities, many=True)
        printed_count = None
        selected_company_id = None
        user = get_user(request)
        print(user)
        if user is not None:
            selected_company = Company.objects.filter(status=1, user=user)
            if selected_company.count() != 0:
                selected_company_id = selected_company[0].id
                printed_count = CompanyUser.objects.filter(company=selected_company_id).count()
        response = {
            "personalities": serializer.data,
            "company_id": selected_company_id,
            "company_count": printed_count
        }
        return Response(response, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(request_body=PersonalitiesSerializer)
    @method_permission_classes([IsAdminAuth])
    def post(self, request):
        parsed_data = JSONParser().parse(request)
        serializer = PersonalitiesSerializer(data=parsed_data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK) 
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class personality_card(APIView):
    @method_permission_classes([AllowAny])
    def get(self, request, id):
        try: 
            personality = Personalities.objects.get(id=id) 
        except Personalities.DoesNotExist: 
            return Response({"message": "Person not found"}, status=status.HTTP_400_BAD_REQUEST)
        serializer = PersonalitiesSerializer(personality)
        response = serializer.data
        return Response(response, status=status.HTTP_200_OK)
    
    @method_permission_classes([IsAdminAuth])
    @swagger_auto_schema(request_body=PersonalitiesSerializer)
    def put(self, request, id):
        try: 
            personality = Personalities.objects.get(id=id) 
        except Personalities.DoesNotExist: 
            return Response({"message": "Person not found"}, status=status.HTTP_400_BAD_REQUEST)
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
    
    @method_permission_classes([IsAdminAuth])
    def delete(self, request, id):
        try: 
            personality = Personalities.objects.get(id=id) 
        except Personalities.DoesNotExist: 
            return Response({"message": "Person not found"}, status=status.HTTP_400_BAD_REQUEST)
        pic_result = del_pic(personality)
        if 'error' in pic_result:
            return Response({"message": pic_result}, status=status.HTTP_400_BAD_REQUEST)
        personality.delete() 
        return Response({"message": "Person was deleted successfully!"}, status=status.HTTP_200_OK)
    
    @method_permission_classes([IsAdminAuth])
    @swagger_auto_schema(request_body=PersonalitiesSerializer)
    def post(self, request, id):
        try: 
            personality = Personalities.objects.get(id=id) 
        except Personalities.DoesNotExist: 
            return Response({"message": "Person not found"}, status=status.HTTP_400_BAD_REQUEST)
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


class companies(APIView):
    @method_permission_classes([IsAuth])
    def get(self, request):
        user = get_user(request)
        if user is None:
            return Response({"message": "no active session"}, status=status.HTTP_400_BAD_REQUEST)
        if user.is_superuser or user.is_staff:
            try:
                parsed_data = JSONParser().parse(request)
                if 'status' in parsed_data.keys() and 'start_date' in parsed_data.keys() and 'end_date' in parsed_data.keys():
                    companies = Company.objects.filter(status=parsed_data['status'],
                                                    created_date__range=(parsed_data['start_date'], parsed_data['end_date']))
                elif 'status' in parsed_data.keys():
                    companies = Company.objects.filter(status=parsed_data['status'])
                elif 'start_date' in parsed_data.keys() and 'end_date' in parsed_data.keys():
                    companies = Company.objects.filter(created_date__range=(parsed_data['start_date'], parsed_data['end_date']),
                                                    status__gte = 3)
                else:
                    companies =  Company.objects.filter(status__gte = 3).order_by('created_date', 'status')
            except:
                companies =  Company.objects.filter(status__gte = 3).order_by('created_date', 'status')
        else:
            companies = Company.objects.filter(user=user)
        if companies.count() == 0:
            companies = None
        serializer = CompanySerializer(companies, many=True)
        response = serializer.data
        return Response(response, status=status.HTTP_200_OK)


class company(APIView):
    @method_permission_classes([IsAuth])
    def get(self, request, id):
        user = get_user(request)
        try: 
            company = Company.objects.get(id=id, user=user) 
        except Company.DoesNotExist: 
            return Response("cant get id", status=status.HTTP_400_BAD_REQUEST)
        serializer = CartSerializer(company)
        response = serializer.data
        return Response(response, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(request_body=EditCartSerializer)
    @method_permission_classes([IsAuth])
    def put(self, request, id):
        user = get_user(request)
        try: 
            company = Company.objects.get(id=id, user=user) 
        except Company.DoesNotExist: 
            return Response("cant get id", status=status.HTTP_400_BAD_REQUEST)
        parsed_data = JSONParser().parse(request)
        serializer = EditCartSerializer(company, data=parsed_data, partial=True) 
        if serializer.is_valid(): 
            serializer.save() 
            return Response(serializer.data) 
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 
    
    @method_permission_classes([IsAuth])
    def delete(self, request, id):
        user = get_user(request)
        try: 
            company = Company.objects.get(id=id, user=user) 
        except Company.DoesNotExist: 
            return Response("cant get id", status=status.HTTP_400_BAD_REQUEST)
        company.status = 2
        company.save() 
        return Response({"message": "Company was deleted successfully!"}, status=status.HTTP_200_OK)
 

@swagger_auto_schema(method='post', request_body=ItemsSerializer)
@api_view(["POST"])
@permission_classes([IsAuth])
def add_item(request, id):
    selected_user = get_user(request)
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


@swagger_auto_schema(method='post', request_body=UserSerializer)
@csrf_exempt
@api_view(["POST"])
@permission_classes([AllowAny])
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


@swagger_auto_schema(method='put', request_body=EditUserSerializer)
@api_view(["PUT"])
@permission_classes([IsAuth])
def user_edit(request):
    parsed_data = JSONParser().parse(request)
    if request.method == 'PUT':
        try:
            user = User.objects.get(username = parsed_data['username'], password = parsed_data['password'])
        except User.DoesNotExist:
            return Response({"message": "Cant login"}, status=status.HTTP_400_BAD_REQUEST)
        serializer = EditUserSerializer(user, data=parsed_data, partial=True)
        if serializer.is_valid():
            serializer.save()
        else:
            return Response({"message": "Bad data"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data, status=status.HTTP_200_OK)


@swagger_auto_schema(method='post', request_body=UserSerializer)
@api_view(["POST"])
@permission_classes([AllowAny])
@authentication_classes([])
def user_auth(request):
    username = request.data.get("username")
    password = request.data.get("password")
    user = authenticate(request, username=username,
                            password=password)
    if user is not None:
        login(request, user)
        random_key = str(uuid.uuid4())
        session_storage.set(random_key, username)
        response = Response(status=status.HTTP_200_OK)
        response.set_cookie("session_id", random_key, samesite="lax")
        return response
    else:
        return Response({"message": "Cant login",
                             "username":username,
                             "password":password},
                            status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(method='post')
@api_view(["POST"])
def user_deauth(request):
    session_id = request.COOKIES.get("session_id")
    if session_id is not None:
        session_storage.delete(session_id)
    logout(request._request)
    return Response({'message': 'Success'})


@swagger_auto_schema(method='post')
@api_view(["POST"])
@permission_classes([IsAuth])
def submit_company(request, id):
    user = get_user(request)
    try: 
        company = Company.objects.get(id=id, status=1, user=user) 
    except Company.DoesNotExist: 
        return Response("cant get id", status=status.HTTP_400_BAD_REQUEST)
    if company.company_name != None and company.description != None:
        company.status = 3
        company.submited_date = datetime.datetime.now()
        company.save()
        serializers = CartSerializer(company)
        return Response(serializers.data, status=status.HTTP_200_OK)
    return Response({"message": "Not valid"}, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(method='post')
@api_view(["POST"])
@permission_classes([IsManagerAuth])
def accept_company(request, id):
    user = get_user(request)
    try: 
        company = Company.objects.get(id=id, status=3) 
    except Company.DoesNotExist: 
        return Response({"message": "Company not found"}, status=status.HTTP_200_OK)
    if company.company_name != None and company.description != None and company.submited_date != None:
        company.status = 4
        company.accepted_date = datetime.datetime.now()
        company.moderator = user
        company.save()
        serializers = CartSerializer(company)
        return Response(serializers.data, status=status.HTTP_200_OK)
    return Response({"message": "Not valid"}, status=status.HTTP_400_BAD_REQUEST)


class company_user(APIView):
    @swagger_auto_schema(request_body=ItemsSerializer)
    @method_permission_classes([IsAuth])
    def put(self, request, id):
        user = user(request)
        try: 
            item = CompanyUser.objects.get(id=id, company__user=user) 
        except CompanyUser.DoesNotExist: 
            return Response({"message": "cant get item"}, status=status.HTTP_200_OK)
        parsed_data = JSONParser().parse(request)
        serializer = ItemsSerializer(item, data=parsed_data, partial=True)
        if serializer.is_valid():
            serializer.save()
        else:
            return Response({"message": "Not valid"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @method_permission_classes([IsAuth])
    def delete(self, request, id):
        user = user(request)
        try: 
            item = CompanyUser.objects.get(id=id, company__user=user) 
        except CompanyUser.DoesNotExist: 
            return Response({"message": "cant get item"}, status=status.HTTP_200_OK)
        item.delete()
        return Response({"message": "Deleted succesfuly"}, status=status.HTTP_200_OK)