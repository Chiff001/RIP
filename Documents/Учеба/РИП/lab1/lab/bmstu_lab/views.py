from django.shortcuts import render


cart_id = [0, 1, 2]
data = [
        {'name': 'ООО "Интернет решения"', 'description': 'Компании: Ozon', 'type': 'Юридическое лицо', 'id': 0, 'image': 'http://localhost:9000/lab1/1.jpeg'},
        {'name': 'Гейль Александр Владимирович', 'description': 'Генеральный Директор ООО "Интернет решения", доля акций: 51%', 'type': 'Физическое лицо', 'id': 1, 'image': 'http://localhost:9000/lab1/Geyl.jpg'},
        {'name': 'Петров Петр Петрович', 'description': 'Заместитель Генерального Директора ООО "Интернет решения", доля акций: 12%', 'type': 'Физическое лицо', 'id': 2, 'image': 'http://localhost:9000/lab1/Petrov.jpg'},
        {'name': 'ООО "Вайлдберриз"           ', 'description': 'Компании: Wildberries', 'type': 'Юридическое лицо', 'id': 3, 'image': 'http://localhost:9000/lab1/2.png'},
        {'name': 'Бакальчук Татьяна Владимировна', 'description': 'Генеральный Директор ООО "Вайлдберриз", доля акций: 63%', 'type': 'Физическое лицо', 'id': 4, 'image': 'http://localhost:9000/lab1/Bak.jpg'},
        {'name': 'Иванов Иван Иванович', 'description': 'Заместитель Генерального Директора ООО "Вайлдберриз", доля акций: 12%', 'type': 'Физическое лицо', 'id': 5, 'image': 'http://localhost:9000/lab1/Ivanov.jpg'},
    ]


def GetCards(request):
    return render(request, 'start.html', {
        'data': data
    })

def GetCard(request, id):
    return render(request, 'info.html', data[id])

def GetKorz(request):
    UR = []
    FIZ = []
    for i in data:
        if i['id'] in cart_id and UR == []:
            UR.append(i)
        elif i['id'] in cart_id:
            FIZ.append(i)
    return render(request, 'korz.html', {'cards_UR': UR, 'cards_FIZ': FIZ})

def SearchCards(request):
    input_text = str(request.POST['text'])
    result = []
    for i in data:
        if input_text in i['name']:
            result.append(i)
    return render(request, 'start.html', {
        'data': result,
        'search_text': input_text
    })