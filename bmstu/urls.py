from django.contrib import admin
from django.urls import path
from bmstu_lab import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.GetPersonalities, name='search'),
    path('Personalities/<int:selected_id>', views.GetPersonalitiesInformation, name='card_url'),
    path('Company/<int:id>', views.GetCompany, name='Company'),
    path('Add_to_company/', views.AddPersonalities),
    path('Company/<int:selected_id>/Del_company/', views.DelCompany, name='card_del')
]