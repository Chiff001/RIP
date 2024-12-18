from django.contrib import admin

from .models import *

admin.site.register(Personality)
admin.site.register(Company)
admin.site.register(PersonalityCompany)
