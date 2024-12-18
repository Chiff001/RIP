from rest_framework import serializers

from .models import *


class PersonalitysSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    def get_image(self, personality):
        if personality.image:
            return personality.image.url.replace("minio", "localhost", 1)

        return "http://localhost:9000/images/default.png"

    class Meta:
        model = Personality
        fields = ("id", "name", "status", "type", "number", "image")


class PersonalitySerializer(PersonalitysSerializer):
    class Meta:
        model = Personality
        fields = "__all__"


class PersonalityAddSerializer(serializers.ModelSerializer):
    class Meta:
        model = Personality
        fields = ("name", "description", "type", "number", "image")


class CompanysSerializer(serializers.ModelSerializer):
    owner = serializers.StringRelatedField(read_only=True)
    moderator = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Company
        fields = "__all__"


class CompanySerializer(CompanysSerializer):
    personalitys = serializers.SerializerMethodField()

    def get_personalitys(self, company):
        items = PersonalityCompany.objects.filter(company=company)
        return [PersonalityItemSerializer(item.personality, context={"count": item.count}).data for item in items]


class PersonalityItemSerializer(PersonalitySerializer):
    count = serializers.SerializerMethodField()

    def get_count(self, _):
        return self.context.get("count")

    class Meta:
        model = Personality
        fields = ("id", "name", "status", "type", "number", "image", "count")


class PersonalityCompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonalityCompany
        fields = "__all__"


class UpdateCompanyStatusAdminSerializer(serializers.Serializer):
    status = serializers.IntegerField(required=True)

    
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', "is_superuser")


class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'password', 'username')
        write_only_fields = ('password',)
        read_only_fields = ('id',)

    def create(self, validated_data):
        user = User.objects.create(
            email=validated_data['email'],
            username=validated_data['username']
        )

        user.set_password(validated_data['password'])
        user.save()

        return user


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)


class UserProfileSerializer(serializers.Serializer):
    username = serializers.CharField(required=False)
    email = serializers.CharField(required=False)
    password = serializers.CharField(required=False)
