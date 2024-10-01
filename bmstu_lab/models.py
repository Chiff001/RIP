from django.db import models

class Personalities(models.Model):
    name = models.CharField(max_length=255)  # ФИО/Название ООО
    number = models.IntegerField()  # ИНН/ОГРН
    info = models.TextField(blank=True)  # Описание
    description = models.TextField(blank=True)  # Ключевая информация
    type = models.TextField()  # Тип лица
    image = models.TextField() # URL изображения 

    class Meta:
        db_table = 'Personalities'


class CompanyApp(models.Model):
    company_name = models.TextField(blank=True)  # Имя компании

    class Meta:
        db_table = 'CompanyApp'


class CompanyUser(models.Model):
    company = models.ForeignKey(CompanyApp, on_delete=models.CASCADE)  # Связь с заказом
    user_id = models.ForeignKey(Personalities, on_delete=models.CASCADE)
    dolya = models.IntegerField()  # Доля акций

    class Meta:
        db_table = 'CompanyUser'
