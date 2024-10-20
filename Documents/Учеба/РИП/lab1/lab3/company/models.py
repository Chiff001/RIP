from django.db import models

class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField(default=False)
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'auth_user'


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
    user = models.ForeignKey('AuthUser', on_delete=models.DO_NOTHING, null=True, blank=False, related_name='company')
    moderator = models.ForeignKey('AuthUser', on_delete=models.DO_NOTHING, null=True, blank=False, related_name='m_company')

    class Meta:
        db_table = 'CompanyApp'


class CompanyUser(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)  # Связь с заказом
    user_id = models.ForeignKey(Personalities, on_delete=models.CASCADE, related_name='users')
    kol_akc = models.IntegerField()  # Кол-во акций

    class Meta:
        db_table = 'CompanyUser'