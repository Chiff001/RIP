from django.shortcuts import render
from bmstu_lab.models import *
import datetime

def GetPersonalities(request):
    personalities_name = request.POST.get("personalities-name")
    printed_count = 0
    selected_company_id = 0
    selected_company = Company.objects.filter(status=1)
    print(request.POST.get("personalities-name"))
    if selected_company.count() != 0:
        selected_company_id = selected_company[0].id
        printed_count = CompanyUser.objects.filter(company=selected_company_id).count()
    if personalities_name != None:
        result = []
        for i in Personalities.objects.all():
            if personalities_name in i.name:
                result.append(i)
        return render(request, 'start.html', {
            'data': result,
            'personalities_name': personalities_name,
            'count': printed_count,
            'company_id' : selected_company_id
        })
    return render(request, 'start.html', {
        'data': Personalities.objects.all(),
        'count': printed_count,
        'company_id' : selected_company_id
    })


def GetPersonalitiesInformation(request, selected_id):
    printed_count = 0
    selected_company_id = 0
    selected_company = Company.objects.filter(status=1)
    if selected_company.count() != 0:
        selected_company_id = selected_company[0].id
        printed_count = CompanyUser.objects.filter(company=selected_company_id).count()
    return render(request, 'info.html', {
        'data': Personalities.objects.filter(id=selected_id),
        'count': printed_count,
        'company_id' : selected_company_id})
# Create your views here.

def GetCompany(request, id):
    selected_company = Company.objects.filter(status=1)
    company_name = ''
    company_description = ''
    if selected_company.count() != 0:
        a = CompanyUser.objects.filter(company=Company.objects.filter(status=1)[0]).select_related('user_id')
        kol_akc = 0
        for i in a:
            kol_akc += i.kol_akc
        company_name = selected_company[0].company_name
        company_description = selected_company[0].description
        return render(request, 'korz.html', {
            'data': CompanyUser.objects.select_related('user_id').filter(company=Company.objects.filter(status=1)[0]),
            'kol_akc': kol_akc,
            'company_id': id,
            'company_name': company_name,
            'company_description': company_description
        })
    return render(request, 'korz.html', {
            'data': [],
            'kol_akc': 0,
            'company_id': 0,
            'company_name': company_name,
            'company_description': company_description
        })

def AddPersonalities(request):
    writing_personalities =request.POST['writing_personalities']
    started_company = Company.objects.filter(status=1).count()
    if started_company == 0:
        new_company = Company(created_date = datetime.date.today(), status = 1)
        new_company.save()
    if CompanyUser.objects.filter(user_id=Personalities.objects.filter(id=writing_personalities)[0],
                                  company=Company.objects.filter(status=1)[0]).count() != 0:
        selected_personality = CompanyUser.objects.filter(company=Company.objects.filter(status=1)[0],
                                                          user_id=Personalities.objects.filter(id=writing_personalities)[0])[0]
        selected_personality.kol_akc += 1
        selected_personality.save()
    else:
        selected_company = Company.objects.filter(status=1)[0]
        selected_personality = Personalities.objects.filter(id=writing_personalities)[0]
        item = CompanyUser(company=selected_company, user_id=selected_personality, kol_akc=1)
        item.save()
    printed_count = 0
    selected_company_id = 0
    selected_company = Company.objects.filter(status=1)
    if selected_company.count() != 0:
        selected_company_id = selected_company[0].id
        printed_count = CompanyUser.objects.filter(company=selected_company_id).count()
    return render(request, 'start.html', {
        'data': Personalities.objects.all(),
        'count': printed_count,
        'company_id' : selected_company_id
    })

def DelCompany(request, selected_id):
    selected_company = Company.objects.filter(status=1)
    if selected_company.count() != 0:
        selected_company = Company.objects.filter(status=1)[0]
        selected_company.status = 2
        selected_company.save()
    printed_count = 0
    selected_company_id = 0
    selected_company = Company.objects.filter(status=1)
    if selected_company.count() != 0:
        selected_company_id = selected_company[0].id
        printed_count = CompanyUser.objects.filter(company=selected_company_id).count()
    return render(request, 'start.html', {
        'data': Personalities.objects.all(),
        'count': printed_count,
        'company_id' : selected_company_id
    })