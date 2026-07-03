from pathlib import Path

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files import File
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from wine_cellar.apps.storage.models import Storage, StorageItem
from wine_cellar.apps.wine.models import (
    Grape,
    ImageType,
    Region,
    Size,
    Vineyard,
    Wine,
    WineImage,
)

DEMO_WINES = (
    (
        "La Croix des Mariniers",
        "WH",
        2020,
        "FR",
        "Condrieu",
        "Georges Vernay",
        ("Viognier",),
        0,
        8,
    ),
    ("Septentrio", "WH", 2021, "FR", "Rhône", "Maison Stéphan", ("Viognier",), 2, 8),
    (
        "Les Hautes Vignes",
        "RE",
        2019,
        "FR",
        "Côtes-du-Rhône",
        "Domaine des Hauts Coteaux",
        ("Syrah", "Grenache"),
        6,
        10,
    ),
    (
        "Clos du Vieux Chêne",
        "RE",
        2018,
        "FR",
        "Margaux",
        "Château Margeaux",
        ("Cabernet Sauvignon", "Merlot"),
        3,
        9,
    ),
    (
        "Cuvée Émeraude",
        "WH",
        2022,
        "FR",
        "Chablis",
        "Domaine Sainte-Anne",
        ("Chardonnay",),
        4,
        8,
    ),
    (
        "Rosa Antica",
        "RO",
        2023,
        "IT",
        "Toscana",
        "Tenuta del Sole",
        ("Sangiovese",),
        0,
        7,
    ),
)


class Command(BaseCommand):
    help = "Create an idempotent six-wine collection for visual development."

    def add_arguments(self, parser):
        parser.add_argument("--username")

    @transaction.atomic
    def handle(self, *args, **options):
        users = get_user_model().objects.all()
        if options["username"]:
            users = users.filter(username=options["username"])
        if users.count() != 1:
            raise CommandError(
                "Pass --username when the database has zero or multiple users."
            )
        user = users.get()
        size, _ = Size.objects.get_or_create(name=0.75, user=None)
        storage, _ = Storage.objects.get_or_create(
            user=user,
            name="Demo cellar",
            defaults={"location": "Home", "rows": 3, "columns": 10},
        )
        assets = Path(settings.ROOT_DIR) / "wine_cellar/assets/images/demo"

        for index, (
            name,
            wine_type,
            vintage,
            country,
            region_name,
            vineyard_name,
            grapes,
            stock,
            rating,
        ) in enumerate(DEMO_WINES):
            region, _ = Region.objects.get_or_create(name=region_name, user=user)
            wine, _ = Wine.objects.update_or_create(
                user=user,
                name=name,
                vintage=vintage,
                defaults={
                    "wine_type": wine_type,
                    "country": country,
                    "region": region,
                    "size": size,
                    "rating": rating,
                },
            )
            vineyard, _ = Vineyard.objects.get_or_create(name=vineyard_name, user=user)
            wine.vineyard.set([vineyard])
            wine.grapes.set(
                [
                    Grape.objects.get_or_create(name=grape, user=user)[0]
                    for grape in grapes
                ]
            )
            image_path = assets / (
                "bottle-red.jpg" if wine_type == "RE" else "bottle-white.jpg"
            )
            if not wine.wineimage_set.exists():
                with image_path.open("rb") as image:
                    WineImage.objects.create(
                        wine=wine,
                        user=user,
                        image=File(image, name=f"demo-{index}.jpg"),
                        image_type=ImageType.FRONT,
                    )
            existing = wine.storageitem_set.filter(deleted=False).count()
            for column in range(existing + 1, stock + 1):
                StorageItem.objects.create(
                    user=user,
                    wine=wine,
                    storage=storage,
                    row=(index // 3) + 1,
                    column=column,
                )

        self.stdout.write(
            self.style.SUCCESS(f"Demo collection ready for {user.username}.")
        )
