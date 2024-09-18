from django.contrib import admin
from django.urls import path
from bmstu_lab import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.GetCards),
    path('pass_url/<int:id>', views.GetCard, name='pass_url'),
    path('cart/', views.GetKorz, name='cart'),
    path('searchPasses', views.SearchCards, name='searchPasses'),
]

