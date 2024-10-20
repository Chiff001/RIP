"""
URL configuration for lab3 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from company import views
from django.urls import include, path
from rest_framework import routers

router = routers.DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
    path(r'personalities/', views.personalities_catalog, name='Personalities-catalog'),
    path(r'companies/', views.companies, name='Companies'),
    path(r'personalities/<int:id>/', views.personality_card, name='Personality-card'),
    #path(r'personalities/<int:id>/put/', views.put, name='Personalities-put'),
    path(r'personalities/<int:id>/add/', views.add_item, name='add-item'),
    path(r'companies/<int:id>/', views.company, name='Company'),
    path(r'companies/<int:id>/submit/', views.submit_company, name='submit-company'),
    path(r'companies/<int:id>/accept/', views.accept_company, name='accept-company'),
    path(r'item/<int:id>/', views.company_user, name='company-user'),
    path(r'user/', views.user_registration, name='registration'),
    path(r'auth/', views.user_auth, name='auth'),
    path(r'logout/', views.user_deauth, name='logout'),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('admin/', admin.site.urls),
]