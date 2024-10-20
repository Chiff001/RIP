from django.db import models

class Personalities(models.Model):
    name = models.CharField(max_length=255)  # ФИО/Название ООО
    number = models.TextField()  # ИНН/ОГРН
    info = models.TextField()  # Описание
    type = models.TextField()  # Тип лица
    image = models.TextField(blank=True) # URL изображения 

    class Meta:
        db_table = 'Personalities'


class Company(models.Model):
    company_name = models.TextField(blank=True)
    description = models.TextField(blank=True)
    accepted_date = models.DateField(blank=True, null=True)
    created_date = models.DateField(blank=True, null=True)
    status = models.IntegerField()
    submited_date = models.DateField(blank=True, null=True)  # Имя компании

    class Meta:
        db_table = 'CompanyApp'


class CompanyUser(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)  # Связь с заказом
    user_id = models.ForeignKey(Personalities, on_delete=models.CASCADE)
    kol_akc = models.IntegerField()  # Кол-во акций

    class Meta:
        db_table = 'CompanyUser'