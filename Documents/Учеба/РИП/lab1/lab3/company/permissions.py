
from rest_framework import permissions
from django.contrib.auth.models import User
from .redis import session_storage
from rest_framework import authentication
from rest_framework import exceptions

class IsManager(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and (request.user.is_staff or request.user.is_superuser))

class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_superuser)

class AuthBySessionID(authentication.BaseAuthentication):
    def authenticate(self, request):
        session_id = request.COOKIES.get("session_id")
        print("COOKIE ", session_id)
        if session_id is None:
            raise exceptions.AuthenticationFailed("Нет сессии")
        try:
            username = session_storage.get(session_id).decode("utf-8")
        except Exception as e:
            raise exceptions.AuthenticationFailed("Сессия с таким ID не найдена в хранилище сессий")
        user = User.objects.get(username=username)
        if user is None:
            raise exceptions.AuthenticationFailed("Нет пользователя с именем, соответствующим сессии, в БД")
        return user, None


class AuthBySessionIDIfExists(authentication.BaseAuthentication):
    def authenticate(self, request):
        session_id = request.COOKIES.get("session_id")
        if session_id is None:
            return None, None
        try:
            username = session_storage.get(session_id).decode("utf-8")
        except Exception as e:
            return None, None
        user = User.objects.get(username=username)
        return user, None


class IsAuth(permissions.BasePermission):
    def has_permission(self, request, view):
        session_id = request.COOKIES.get("session_id")
        if session_id is None:
            return False
        try:
            session_storage.get(session_id).decode("utf-8")
        except Exception as e:
            return False
        return True


class IsManagerAuth(permissions.BasePermission):
    def has_permission(self, request, view):
        session_id = request.COOKIES.get("session_id")
        print("MODERATOR")
        if session_id is None:
            return False
        try:
            username = session_storage.get(session_id).decode("utf-8")
        except Exception as e:
            return False
        user = User.objects.get(username=username)
        if user is None:
            return False
        print(user.is_staff)
        return user.is_staff or user.is_superuser


class IsAdminAuth(permissions.BasePermission):
    def has_permission(self, request, view):
        session_id = request.COOKIES.get("session_id")
        print("COOKIE ADMIN", session_id)
        if session_id is None:
            return False
        try:
            username = session_storage.get(session_id).decode("utf-8")
        except Exception as e:
            return False
        user = User.objects.get(username=username)
        if user is None:
            return False
        return user.is_superuser
