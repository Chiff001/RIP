from django.urls import path
from .views import *

urlpatterns = [
    # Набор методов для услуг
    path('api/personalitys/', search_personalitys),  # GET
    path('api/personalitys/<int:personality_id>/', get_personality_by_id),  # GET
    path('api/personalitys/<int:personality_id>/update/', update_personality),  # PUT
    path('api/personalitys/<int:personality_id>/update_image/', update_personality_image),  # POST
    path('api/personalitys/<int:personality_id>/delete/', delete_personality),  # DELETE
    path('api/personalitys/create/', create_personality),  # POST
    path('api/personalitys/<int:personality_id>/add_to_company/', add_personality_to_company),  # POST

    # Набор методов для заявок
    path('api/companys/', search_companys),  # GET
    path('api/companys/<int:company_id>/', get_company_by_id),  # GET
    path('api/companys/<int:company_id>/update/', update_company),  # PUT
    path('api/companys/<int:company_id>/update_status_user/', update_status_user),  # PUT
    path('api/companys/<int:company_id>/update_status_admin/', update_status_admin),  # PUT
    path('api/companys/<int:company_id>/delete/', delete_company),  # DELETE

    # Набор методов для м-м
    path('api/companys/<int:company_id>/update_personality/<int:personality_id>/', update_personality_in_company),  # PUT
    path('api/companys/<int:company_id>/delete_personality/<int:personality_id>/', delete_personality_from_company),  # DELETE

    # Набор методов для аутентификации и авторизации
    path("api/users/register/", register),  # POST
    path("api/users/login/", login),  # POST
    path("api/users/logout/", logout),  # POST
    path("api/users/<int:user_id>/update/", update_user)  # PUT
]
