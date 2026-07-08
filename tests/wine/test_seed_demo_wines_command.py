import pytest
from django.core.management import call_command

from wine_cellar.apps.storage.models import Storage, StorageItem
from wine_cellar.apps.wine.models import Wine


@pytest.mark.django_db
def test_seed_demo_wines_creates_requested_collection_for_email(
    user,
    clear_image_folder,
):
    call_command("seed_demo_wines", email=user.email, count=20, seed=12)

    wines = Wine.objects.filter(user=user)
    storage_items = StorageItem.objects.filter(user=user, deleted=False)
    storage = Storage.objects.get(user=user, name="Demo cellar")

    assert wines.count() == 20
    assert storage_items.count() >= 20
    assert storage.rows * storage.columns >= storage_items.count()
    assert wines.filter(wineimage__isnull=False).distinct().count() == 20

    stock_count = storage_items.count()
    call_command("seed_demo_wines", email=user.email, count=20, seed=12)

    assert Wine.objects.filter(user=user).count() == 20
    assert StorageItem.objects.filter(user=user, deleted=False).count() == stock_count


@pytest.mark.django_db
def test_seed_demo_wines_can_create_exact_bottle_count(user, clear_image_folder):
    call_command(
        "seed_demo_wines",
        username=user.username,
        count=20,
        bottles=20,
        seed=12,
    )

    assert Wine.objects.filter(user=user).count() == 20
    assert StorageItem.objects.filter(user=user, deleted=False).count() == 20
