from rest_framework import serializers
from company.models import *

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ["id", "company_name", "description", "created_date", "submited_date", "accepted_date", "status", "user", "moderator"]


class PersonalitiesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Personalities
        fields = ["id", "name", "number", "info", "type", "image", "status"]


class CompanyUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Personalities
        fields = ["id", "name", "info"]


class ItemsSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user_id.name')
    user_number = serializers.CharField(source='user_id.number')
    user_image = serializers.CharField(source='user_id.image')
    class Meta:
        model = CompanyUser
        fields = ["user_name", "user_number", "user_image", "kol_akc", "id"]
    

class CartSerializer(serializers.ModelSerializer):
    users = ItemsSerializer(many=True, read_only=True)
    class Meta:
        model = Company
        fields = ["id", "company_name", "description", "created_date", "submited_date", "accepted_date", "status", "users"]


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuthUser
        fields = ["username", "password", "email"]


class EditUserSerializer(serializers.ModelSerializer):
    companies = CartSerializer(many=True, read_only=True)
    class Meta:
        model = AuthUser
        fields = ["first_name", "last_name", "email", "password", "companies"]


class EditCartSerializer(serializers.ModelSerializer):
    companies = ItemsSerializer(many=True, read_only=True)
    class Meta:
        model = Company
        fields = ["company_name", "description", "created_date", "companies"]

class EditItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyUser
        fields = ["id", "company", "user_id", "kol_akc"]