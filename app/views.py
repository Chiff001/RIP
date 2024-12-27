import random
from datetime import datetime, timedelta
import uuid
import hashlib

from django.contrib.auth import authenticate
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response

from .permissions import *
from .redis import session_storage
from .serializers import *
from .utils import identity_user, get_session

import string
import random


def get_draft_company(request):
    user = identity_user(request)

    if user is None:
        return None

    company = Company.objects.filter(owner=user).filter(status=1).first()

    return company


@swagger_auto_schema(
    method='get',
    manual_parameters=[
        openapi.Parameter(
            'personality_name',
            openapi.IN_QUERY,
            type=openapi.TYPE_STRING
        )
    ]
)
@api_view(["GET"])
def search_personalitys(request):
    personality_name = request.GET.get("personality_name", "")

    personalitys = Personality.objects.filter(status=1)

    if personality_name:
        personalitys = personalitys.filter(name__icontains=personality_name)

    serializer = PersonalitysSerializer(personalitys, many=True)

    draft_company = get_draft_company(request)

    resp = {
        "personalitys": serializer.data,
        "personalitys_count": PersonalityCompany.objects.filter(company=draft_company).count() if draft_company else None,
        "draft_company_id": draft_company.pk if draft_company else None
    }

    return Response(resp)


@api_view(["GET"])
def get_personality_by_id(request, personality_id):
    if not Personality.objects.filter(pk=personality_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    personality = Personality.objects.get(pk=personality_id)
    serializer = PersonalitySerializer(personality)

    return Response(serializer.data)


@swagger_auto_schema(method='put', request_body=PersonalitySerializer)
@api_view(["PUT"])
@permission_classes([IsModerator])
def update_personality(request, personality_id):
    if not Personality.objects.filter(pk=personality_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    personality = Personality.objects.get(pk=personality_id)

    serializer = PersonalitySerializer(personality, data=request.data)

    if serializer.is_valid(raise_exception=True):
        serializer.save()

    return Response(serializer.data)


@swagger_auto_schema(method='POST', request_body=PersonalityAddSerializer)
@api_view(["POST"])
@permission_classes([IsModerator])
@parser_classes((MultiPartParser,))
def create_personality(request):
    serializer = PersonalityAddSerializer(data=request.data)

    serializer.is_valid(raise_exception=True)

    Personality.objects.create(**serializer.validated_data)

    personalitys = Personality.objects.filter(status=1)
    serializer = PersonalitysSerializer(personalitys, many=True)

    return Response(serializer.data)


@api_view(["DELETE"])
@permission_classes([IsModerator])
def delete_personality(request, personality_id):
    if not Personality.objects.filter(pk=personality_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    personality = Personality.objects.get(pk=personality_id)
    personality.status = 2
    personality.save()

    personality = Personality.objects.filter(status=1)
    serializer = PersonalitySerializer(personality, many=True)

    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_personality_to_company(request, personality_id):
    if not Personality.objects.filter(pk=personality_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    personality = Personality.objects.get(pk=personality_id)

    draft_company = get_draft_company(request)

    if draft_company is None:
        draft_company = Company.objects.create()
        draft_company.date_created = timezone.now()
        draft_company.owner = identity_user(request)
        draft_company.save()

    if PersonalityCompany.objects.filter(company=draft_company, personality=personality).exists():
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    item = PersonalityCompany.objects.create()
    item.company = draft_company
    item.personality = personality
    item.save()

    serializer = CompanySerializer(draft_company)
    return Response(serializer.data["personalitys"])


@swagger_auto_schema(
    method='post',
    manual_parameters=[
        openapi.Parameter('image', openapi.IN_FORM, type=openapi.TYPE_FILE),
    ]
)
@api_view(["POST"])
@permission_classes([IsModerator])
@parser_classes((MultiPartParser,))
def update_personality_image(request, personality_id):
    if not Personality.objects.filter(pk=personality_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    personality = Personality.objects.get(pk=personality_id)

    image = request.data.get("image")

    if image is None:
        return Response(status.HTTP_400_BAD_REQUEST)

    personality.image = image
    personality.save()

    serializer = PersonalitySerializer(personality)

    return Response(serializer.data)


@swagger_auto_schema(
    method='get',
    manual_parameters=[
        openapi.Parameter(
            'status',
            openapi.IN_QUERY,
            type=openapi.TYPE_NUMBER
        ),
        openapi.Parameter(
            'date_formation_start',
            openapi.IN_QUERY,
            type=openapi.TYPE_STRING
        ),
        openapi.Parameter(
            'date_formation_end',
            openapi.IN_QUERY,
            type=openapi.TYPE_STRING
        )
    ]
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def search_companys(request):
    status_id = int(request.GET.get("status", 0))
    date_formation_start = request.GET.get("date_formation_start")
    date_formation_end = request.GET.get("date_formation_end")

    companys = Company.objects.exclude(status__in=[1, 5])

    user = identity_user(request)
    if not user.is_superuser:
        companys = companys.filter(owner=user)

    if status_id > 0:
        companys = companys.filter(status=status_id)

    if date_formation_start and parse_datetime(date_formation_start):
        companys = companys.filter(date_formation__gte=parse_datetime(date_formation_start) - timedelta(days=1))

    if date_formation_end and parse_datetime(date_formation_end):
        companys = companys.filter(date_formation__lt=parse_datetime(date_formation_end) + timedelta(days=1))

    serializer = CompanysSerializer(companys, many=True)

    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_company_by_id(request, company_id):
    user = identity_user(request)

    if not Company.objects.filter(pk=company_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    company = Company.objects.get(pk=company_id)

    if not user.is_superuser and company.owner != user:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = CompanySerializer(company)

    return Response(serializer.data)


@swagger_auto_schema(method='put', request_body=CompanySerializer)
@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_company(request, company_id):
    user = identity_user(request)

    if not Company.objects.filter(pk=company_id, owner=user).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    company = Company.objects.get(pk=company_id)
    serializer = CompanySerializer(company, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()

    return Response(serializer.data)


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_status_user(request, company_id):
    user = identity_user(request)

    if not Company.objects.filter(pk=company_id, owner=user).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    company = Company.objects.get(pk=company_id)

    if company.status != 1:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    company.status = 2
    company.date_formation = timezone.now()
    company.save()

    serializer = CompanySerializer(company)

    return Response(serializer.data)


@swagger_auto_schema(method='put', request_body=UpdateCompanyStatusAdminSerializer)
@api_view(["PUT"])
@permission_classes([IsModerator])
def update_status_admin(request, company_id):
    if not Company.objects.filter(pk=company_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    request_status = int(request.data["status"])

    if request_status not in [3, 4]:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    company = Company.objects.get(pk=company_id)

    if company.status != 2:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    if request_status == 3:
        company.accreditation = random.randint(1, 2)

    company.status = request_status
    company.date_complete = timezone.now()
    company.moderator = identity_user(request)
    company.save()

    serializer = CompanySerializer(company)

    return Response(serializer.data)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_company(request, company_id):
    user = identity_user(request)

    if not Company.objects.filter(pk=company_id, owner=user).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    company = Company.objects.get(pk=company_id)

    if company.status != 1:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    company.status = 5
    company.save()

    return Response(status=status.HTTP_200_OK)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_personality_from_company(request, company_id, personality_id):
    user = identity_user(request)

    if not Company.objects.filter(pk=company_id, owner=user).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    if not PersonalityCompany.objects.filter(company_id=company_id, personality_id=personality_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    item = PersonalityCompany.objects.get(company_id=company_id, personality_id=personality_id)
    item.delete()

    company = Company.objects.get(pk=company_id)

    serializer = CompanySerializer(company)
    personalitys = serializer.data["personalitys"]

    return Response(personalitys)


@swagger_auto_schema(method='PUT', request_body=PersonalityCompanySerializer)
@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_personality_in_company(request, company_id, personality_id):
    user = identity_user(request)

    if not Company.objects.filter(pk=company_id, owner=user).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    if not PersonalityCompany.objects.filter(personality_id=personality_id, company_id=company_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    item = PersonalityCompany.objects.get(personality_id=personality_id, company_id=company_id)

    serializer = PersonalityCompanySerializer(item, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()

    return Response(serializer.data)


@swagger_auto_schema(method='post', request_body=UserLoginSerializer)
@api_view(["POST"])
def login(request):
    serializer = UserLoginSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)

    user = authenticate(**serializer.data)
    if user is None:
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    session_id = str(uuid.uuid4())
    session_storage.set(session_id, user.id)

    serializer = UserSerializer(user)
    response = Response(serializer.data, status=status.HTTP_200_OK)
    response.set_cookie("session_id", session_id, samesite="lax")

    return response


@swagger_auto_schema(method='post', request_body=UserRegisterSerializer)
@api_view(["POST"])
def register(request):
    serializer = UserRegisterSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(status=status.HTTP_409_CONFLICT)

    user = serializer.save()

    session_id = hash_log(user.username, user.password)
    session_storage.set(session_id, user.id)

    serializer = UserSerializer(user)
    response = Response(serializer.data, status=status.HTTP_201_CREATED)
    response.set_cookie("session_id", session_id, samesite="lax")

    return response


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout(request):
    session = get_session(request)
    session_storage.delete(session)

    response = Response(status=status.HTTP_200_OK)
    response.delete_cookie('session_id')

    return response


@swagger_auto_schema(method='PUT', request_body=UserProfileSerializer)
@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_user(request, user_id):
    if not User.objects.filter(pk=user_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    user = identity_user(request)

    if user.pk != user_id:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = UserSerializer(user, data=request.data, partial=True)
    if not serializer.is_valid():
        return Response(status=status.HTTP_409_CONFLICT)

    serializer.save()

    password = request.data.get("password", None)
    if password is not None and not user.check_password(password):
        user.set_password(password)
        user.save()

    return Response(serializer.data, status=status.HTTP_200_OK)


def generate_salt(length=16):
    """Генерация случайной соли."""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))


def hash_log(username, password):
    input_string = f"{id}{username}{password}"

    if not salt:
        salt = generate_salt()

    combined = input_string + salt
    
    unique_hash = hash(combined)

    return unique_hash
