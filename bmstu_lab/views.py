from django.shortcuts import render
from bmstu_lab.models import *


cart_id = [0, 1, 2]
data = [
        {'name': 'ООО "Интернет решения"', 
         'number': 'Номер ОГРН: 1027739244741',
         'info': 'Основное детище: Ozon («Озо́н») — российский маркетплейс. Основан в 1998 году как интернет-магазин по продаже книг и видеокассет. Помимо торговой площадки, компания развивает экспресс-доставку товаров повседневного спроса Ozon fresh, доставку товаров из-за рубежа Ozon Global, финансовые сервисы от Ozon Банк, а также бронирование авиа и железнодорожных билетов, отелей и туров Ozon Travel.',
         'description': 'Компании: Ozon', 'type': 'Юридическое лицо', 'id': 0, 'image': 'http://localhost:9000/lab1/1.jpeg'},
         
        {'name': 'Гейль Александр Владимирович',
         'number': 'Номер ИНН: 660402078756',
         'info': 'Генеральный Директор ООО "Интернет решения". Организации, в отношении которых упоминается данное лицо, зарегистрированы в регионе Москва (торговля розничная, осуществляемая непосредственно при помощи информационно-коммуникационной сети Интернет; деятельность по складированию и хранению).',
         'description': 'Доля акций: 51%', 'type': 'Физическое лицо', 'id': 1, 'image': 'http://localhost:9000/lab1/Geyl.jpeg'},

        {'name': 'Петров Петр Петрович',
         'number': 'Номер ИНН: 670981456782',
         'info': 'Заместитель Генерального Директора ООО "Интернет решения". Информации про Петра Петровича очень мало.',
         'description': 'Доля акций: 12%', 'type': 'Физическое лицо', 'id': 2, 'image': 'http://localhost:9000/lab1/Petrov.jpg'},

        {'name': 'ООО "Вайлдберриз"',
         'number': 'Номер ОГРН: 1067746062449',
         'info': 'Wildberries (Уа́йлдберрис, Ва́йлдберрис; букв. «Дикие ягоды») — российский маркетплейс. Основан в 2004 году Владиславом и Татьяной Бакальчук. Работает в России, Белоруссии, Казахстане, Кыргызстане, Армении, Израиле, Турции, Узбекистане и Азербайджане. Крупнейший по обороту интернет-магазин России в 2016—2020 годах.',
         'description': 'Компании: Wildberries', 'type': 'Юридическое лицо', 'id': 3, 'image': 'http://localhost:9000/lab1/2.png'},

        {'name': 'Бакальчук Татьяна Владимировна',
         'number': 'Номер ИНН: 507203757508',
         'info': 'Татьяна Владимировна Ким (в замужестве Бакальчук; род. 16 октября 1975, Грозный, Чечено-Ингушская АССР) — российская предпринимательница, соосновательница и генеральный директор российского маркетплейса Wildberries. В 2021 году Forbes поставил Татьяну и Владислава Бакальчуков на первое место, среди самых богатых семей России. По данным издания, их имущество оценивалось в 13,1 млрд $. В рейтинге российских миллиардеров за 2024 год, составленном российской версией журнала Forbes, Бакальчук занимает 22-е место с состоянием 7,4 млрд $.',
         'description': 'Доля акций: 63%', 'type': 'Физическое лицо', 'id': 4, 'image': 'http://localhost:9000/lab1/Bak.jpg'},

        {'name': 'Иванов Иван Иванович',
         'number': 'Номер ИНН: 273453900042',
         'info': 'Заместитель Генерального Директора ООО "Вайлдберриз". Информации про Ивана Ивановича очень мало.',
         'description': 'Доля акций: 12%', 'type': 'Физическое лицо', 'id': 5, 'image': 'http://localhost:9000/lab1/Ivanov.jpg'},
    ]


def GetCards(request):
    return render(request, 'start.html', {
        'data': Personalities.objects.all(),
        'count': Application.objects.all().count()
    })

def GetCard(request, sel_id):
    return render(request, 'info.html', {
        'data': Personalities.objects.filter(id=sel_id),
        'count': Application.objects.all().count()
    })

def GetKorz(request):
    UR = []
    FIZ = []
    for i in Application.objects.all():
        for j in Company.objects.all():
            if i.company_app == j:
                UR.append(j)
    if UR != []:
        for i in CompanyUser.objects.all():
            if i.company == UR[0]:
                FIZ.append(i)
    return render(request, 'korz.html', {'cards_UR': UR, 'cards_FIZ': FIZ})

def SearchCards(request):
    input_text = str(request.POST['text'])
    result = []
    for i in Personalities.objects.all():
        if input_text in i.name:
            result.append(i)
    return render(request, 'start.html', {
        'data': result,
        'search_text': input_text
    })

def SearchComp(request):
    input_text = str(request.POST['text'])
    result = []
    for i in Company.objects.all():
        if input_text in i.company_name:
            for i in Company.objects.filter(company_name=i.company_name):
                item = Application(company_app=i)
                item.save()
    return GetKorz(request)

def AddApp(request, sel_id):
    for i in Personalities.objects.filter(id=sel_id):
        comp_name = i.name
    for i in Company.objects.filter(company_name=comp_name):
        item = Application(company_app=i)
        item.save()
    data = {'data': Personalities.objects.filter(id=sel_id)}
    return render(request, 'info.html', data)

def DelApp(request):
    Application.objects.all().delete()
    return render(request, 'korz.html', {'cards_UR': [], 'cards_FIZ': []})