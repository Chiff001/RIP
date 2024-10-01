from django.contrib import admin
from django.urls import path
from bmstu_lab import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.GetCards),
    path('card_url/<int:id>', views.GetCard, name='card_url'),
    path('company/', views.GetKorz, name='company'),
    path('searchOwners', views.SearchCards, name='searchOwners'),
]

