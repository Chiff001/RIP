from django.contrib import admin
from django.urls import path
from bmstu_lab import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.GetCards),
    path('card_url/<int:sel_id>', views.GetCard, name='card_url'),
    path('company/', views.GetKorz, name='company'),
    path('searchOwners/', views.SearchCards, name='searchOwners'),
    path('searchCompanies/', views.SearchComp, name='searchCompanies'),
    path('card_add/<int:sel_id>', views.AddApp, name='card_add'),
    path('card_del/', views.DelApp, name='card_del'),

]

