from pathlib import Path
from random import Random

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

GENERATED_NAME_PREFIXES = (
    "Clos",
    "Domaine",
    "Maison",
    "Chateau",
    "Cave",
    "Terre",
    "Mas",
    "Reserve",
)
GENERATED_NAME_ROOTS = (
    "des Brumes",
    "du Levant",
    "des Roches",
    "du Vieux Pressoir",
    "des Terrasses",
    "de la Combe",
    "du Soleil",
    "des Argiles",
)
GENERATED_PROFILES = (
    ("RE", "FR", "Bordeaux", ("Merlot", "Cabernet Sauvignon")),
    ("RE", "FR", "Bourgogne", ("Pinot Noir",)),
    ("WH", "FR", "Loire", ("Sauvignon Blanc",)),
    ("WH", "FR", "Alsace", ("Riesling",)),
    ("RO", "FR", "Provence", ("Grenache", "Cinsault")),
    ("SP", "IT", "Veneto", ("Glera",)),
    ("RE", "ES", "Rioja", ("Tempranillo",)),
    ("WH", "DE", "Mosel", ("Riesling",)),
)


def build_demo_wines(count, seed):
    wines = list(DEMO_WINES[:count])
    if count <= len(wines):
        return wines

    random = Random(seed)
    for index in range(len(wines), count):
        wine_type, country, region, grapes = random.choice(GENERATED_PROFILES)
        prefix = random.choice(GENERATED_NAME_PREFIXES)
        root = random.choice(GENERATED_NAME_ROOTS)
        vintage = random.randint(2015, 2024)
        wines.append(
            (
                f"{prefix} {root} {index + 1:02d}",
                wine_type,
                vintage,
                country,
                region,
                f"{prefix} {root}",
                grapes,
                random.randint(1, 4),
                random.randint(5, 10),
            )
        )
    return wines


def apply_bottle_count(wines, bottle_count, seed):
    if bottle_count is None:
        return wines
    if bottle_count < 0:
        raise CommandError("--bottles must be zero or greater.")

    random = Random(seed)
    targets = [0] * len(wines)
    for index in range(min(bottle_count, len(targets))):
        targets[index] = 1
    for _index in range(max(bottle_count - len(targets), 0)):
        targets[random.randrange(len(targets))] += 1

    return [
        (
            name,
            wine_type,
            vintage,
            country,
            region_name,
            vineyard_name,
            grapes,
            targets[index],
            rating,
        )
        for index, (
            name,
            wine_type,
            vintage,
            country,
            region_name,
            vineyard_name,
            grapes,
            _stock,
            rating,
        ) in enumerate(wines)
    ]


def next_open_slots(storage, amount):
    occupied = set(
        storage.items.filter(
            deleted=False,
            row__isnull=False,
            column__isnull=False,
        ).values_list("row", "column")
    )
    slots = []
    row = 1
    column = 1
    columns = storage.columns or 10

    while len(slots) < amount:
        if (row, column) not in occupied:
            occupied.add((row, column))
            slots.append((row, column))
        column += 1
        if column > columns:
            row += 1
            column = 1

    if slots and max(row for row, _column in slots) > storage.rows:
        storage.rows = max(row for row, _column in slots)
        storage.save(update_fields=["rows"])

    return slots


class Command(BaseCommand):
    help = "Create a demo wine collection for one user."

    def add_arguments(self, parser):
        parser.add_argument("--username", help="Seed the account with this username.")
        parser.add_argument("--email", help="Seed the account with this email address.")
        parser.add_argument(
            "--count",
            type=int,
            default=len(DEMO_WINES),
            help="Number of wine records to create. Defaults to the curated six wines.",
        )
        parser.add_argument(
            "--bottles",
            type=int,
            help="Total bottles to add in stock across the seeded wines.",
        )
        parser.add_argument(
            "--seed",
            type=int,
            default=2026,
            help="Seed used for deterministic generated wines.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options["count"] < 1:
            raise CommandError("--count must be greater than zero.")
        if options["bottles"] is not None and options["bottles"] < 0:
            raise CommandError("--bottles must be zero or greater.")
        if options["username"] and options["email"]:
            raise CommandError("Pass either --username or --email, not both.")

        users = get_user_model().objects.all()
        if options["username"]:
            users = users.filter(username=options["username"])
        if options["email"]:
            users = users.filter(email__iexact=options["email"])
        if users.count() != 1:
            raise CommandError(
                "Pass --username or --email when the database has zero or "
                "multiple users."
            )
        user = users.get()
        size, _ = Size.objects.get_or_create(name=0.75, user=None)
        storage, _ = Storage.objects.get_or_create(
            user=user,
            name="Demo cellar",
            defaults={"location": "Home", "rows": 3, "columns": 10},
        )
        storage.columns = storage.columns or 10
        generated_rows = (options["count"] * 4 // storage.columns) + 1
        storage.rows = max(storage.rows, 3, generated_rows)
        storage.save(update_fields=["rows", "columns"])
        assets = Path(settings.ROOT_DIR) / "wine_cellar/assets/images/demo"

        demo_wines = build_demo_wines(options["count"], options["seed"])
        demo_wines = apply_bottle_count(
            demo_wines,
            options["bottles"],
            options["seed"],
        )

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
        ) in enumerate(demo_wines):
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
            for row, column in next_open_slots(storage, max(stock - existing, 0)):
                StorageItem.objects.create(
                    user=user,
                    wine=wine,
                    storage=storage,
                    row=row,
                    column=column,
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"Demo collection ready for {user.username} "
                f"({options['count']} wines)."
            )
        )
