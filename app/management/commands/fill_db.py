from django.conf import settings
from django.core.management.base import BaseCommand
from minio import Minio

from .utils import *
from app.models import *


def add_users():
    User.objects.create_user("user", "user@user.com", "1234", first_name="user", last_name="user")
    User.objects.create_user("Ilya", "Ilya@user.com", "1234", first_name="Ilya", last_name="Sidorov")
    User.objects.create_superuser("admin", "admin@admin.com", "admin", first_name="admin", last_name="root")

    for i in range(1, 10):
        User.objects.create_user(f"user{i}", f"user{i}@user.com", "1234", first_name=f"user{i}", last_name=f"user{i}")
        User.objects.create_user(f"Ilya{i}", f"Ilya{i}@user.com", "1234", first_name=f"Ilya{i}", last_name=f"Sidorov{i}")
        User.objects.create_superuser(f"admin{i}", f"admin{i}@admin.com", "admin", first_name=f"admin{i}", last_name=f"admin{i}")


def add_personalitys():
    Personality.objects.create(
        name="ООО 'Интернет решения'",
        description="Основное детище: Ozon («Озо́н») — российский маркетплейс. Основан в 1998 году как интернет-магазин по продаже книг и видеокассет. Помимо торговой площадки, компания развивает экспресс-доставку товаров повседневного спроса Ozon fresh, доставку товаров из-за рубежа Ozon Global, финансовые сервисы от Ozon Банк, а также бронирование авиа и железнодорожных билетов, отелей и туров Ozon Travel.",
        type=2,
        number="Номер ОГРН: 1027739244741",
        image="1.png"
    )

    Personality.objects.create(
        name="ООО 'Вайлдберриз'",
        description="Wildberries (Уа́йлдберрис, Ва́йлдберрис; букв. «Дикие ягоды») — российский маркетплейс. Основан в 2004 году Владиславом и Татьяной Бакальчук. Работает в России, Белоруссии, Казахстане, Кыргызстане, Армении, Израиле, Турции, Узбекистане и Азербайджане. Крупнейший по обороту интернет-магазин России в 2016—2020 годах.",
        type=2,
        number="Номер ОГРН: 1067746062449",
        image="2.png"
    )

    Personality.objects.create(
        name="Бакальчук Татьяна Владимировна",
        description="Татьяна Владимировна Ким (в замужестве Бакальчук; род. 16 октября 1975, Грозный, Чечено-Ингушская АССР) — российская предпринимательница, соосновательница и генеральный директор российского маркетплейса Wildberries. В 2021 году Forbes поставил Татьяну и Владислава Бакальчуков на первое место, среди самых богатых семей России. По данным издания, их имущество оценивалось в 13,1 млрд $. В рейтинге российских миллиардеров за 2024 год, составленном российской версией журнала Forbes, Бакальчук занимает 22-е место с состоянием 7,4 млрд $.",
        type=1,
        number="Номер ИНН: 507203757508",
        image="3.png"
    )

    Personality.objects.create(
        name="Гейль Александр Владимирович",
        description="Генеральный Директор ООО 'Интернет решения'. Организации, в отношении которых упоминается данное лицо, зарегистрированы в регионе Москва (торговля розничная, осуществляемая непосредственно при помощи информационно-коммуникационной сети Интернет; деятельность по складированию и хранению).",
        type=1,
        number="Номер ИНН: 660402078756",
        image="4.png"
    )

    Personality.objects.create(
        name="ООО 'Яндекс Маркет'",
        description="«Яндекс Маркет» — электронная торговая площадка (маркетплейс), сервис для покупки товаров. Пользователь «Маркета» может просматривать и покупать товары из различных категорий, сравнивать их характеристики и цены, читать и оставлять отзывы и обзоры на товары, задавать вопросы другим посетителям сайта, магазинам и производителям. Сервис берет на себя хранение товаров, обработку и доставку заказов и общение с покупателями",
        type=2,
        number="Номер ОГРН: 1167746491395",
        image="5.png"
    )

    Personality.objects.create(
        name="Гришаков Максим Петрович",
        description="С мая 2017 года занимает пост генерального директора сервиса Яндекс.Маркет",
        type=1,
        number="Номер ИНН: 773461070263",
        image="6.png"
    )

    client = Minio(settings.MINIO_ENDPOINT,
                   settings.MINIO_ACCESS_KEY,
                   settings.MINIO_SECRET_KEY,
                   secure=settings.MINIO_USE_HTTPS)

    for i in range(1, 7):
        client.fput_object(settings.MINIO_MEDIA_FILES_BUCKET, f'{i}.png', f"app/static/images/{i}.png")

    client.fput_object(settings.MINIO_MEDIA_FILES_BUCKET, 'default.png', "app/static/images/default.png")


def add_companys():
    users = User.objects.filter(is_staff=False)
    moderators = User.objects.filter(is_staff=True)
    personalitys = Personality.objects.all()

    for _ in range(30):
        status = random.randint(2, 5)
        owner = random.choice(users)
        add_company(status, personalitys, owner, moderators)

    add_company(1, personalitys, users[0], moderators)
    add_company(2, personalitys, users[0], moderators)
    add_company(3, personalitys, users[0], moderators)
    add_company(4, personalitys, users[0], moderators)
    add_company(5, personalitys, users[0], moderators)


def add_company(status, personalitys, owner, moderators):
    company = Company.objects.create()
    company.status = status

    if status in [3, 4]:
        company.moderator = random.choice(moderators)
        company.date_complete = random_date()
        company.date_formation = company.date_complete - random_timedelta()
        company.date_created = company.date_formation - random_timedelta()
    else:
        company.date_formation = random_date()
        company.date_created = company.date_formation - random_timedelta()

    if status == 3:
        company.accreditation = random.randint(1, 2)

    company.name = "Название компании"
    company.description = "Описание компании"

    company.owner = owner

    for personality in random.sample(list(personalitys), 3):
        item = PersonalityCompany(
            company=company,
            personality=personality,
            count=random.randint(1, 10)
        )
        item.save()

    company.save()


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        add_users()
        add_personalitys()
        add_companys()
