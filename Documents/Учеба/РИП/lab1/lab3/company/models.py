from django.db import models
from django.contrib.auth.models import User


class Personalities(models.Model):
    name = models.CharField(max_length=255)  # ФИО/Название ООО
    number = models.TextField()  # ИНН/ОГРН
    info = models.TextField()  # Описание
    type = models.TextField()  # Тип лица
    image = models.TextField(blank=True) # URL изображения 
    status = models.BooleanField(default=True) 

    class Meta:
        db_table = 'Personalities'


class Company(models.Model):
    company_name = models.TextField(blank=True)
    description = models.TextField(blank=True)
    accepted_date = models.DateTimeField(blank=True, null=True)
    created_date = models.DateTimeField(blank=True, null=True, auto_now_add=True)
    status = models.IntegerField(default=1)
    submited_date = models.DateTimeField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True, blank=False, related_name='company')
    moderator = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True, blank=False, related_name='m_company')

    class Meta:
        db_table = 'CompanyApp'


class CompanyUser(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)  # Связь с заказом
    user_id = models.ForeignKey(Personalities, on_delete=models.CASCADE, related_name='users')
    kol_akc = models.IntegerField()  # Кол-во акций

    class Meta:
        db_table = 'CompanyUser'