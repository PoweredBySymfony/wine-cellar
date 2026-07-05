import json
from http import HTTPStatus

import pytest
from django.test import override_settings
from django.urls import reverse
from pytest_django.asserts import assertRedirects, assertTemplateUsed


@pytest.mark.django_db
def test_wine_map_view(client, user, wine_factory):
    wine_factory(user=user)
    client.force_login(user)
    r = client.get(reverse("wine-map"))
    assert r.status_code == HTTPStatus.OK
    assertTemplateUsed(response=r, template_name="wine_map.html")


@pytest.mark.django_db
def test_health_check(client):
    r = client.get(reverse("health_check"))
    assert r.status_code == HTTPStatus.OK
    data = json.loads(r.content)
    assert data["status"] == "ok"


@pytest.mark.django_db
@override_settings(AI_MODEL="test-model", AI_API_KEY="test-key")
def test_scan_page_exposes_ai_capture(client, user):
    client.force_login(user)
    response = client.get(reverse("wine-scan"))
    assert response.status_code == HTTPStatus.OK
    assert response.context_data["ai_enabled"] is True
    assert b'data-label-capture="true"' in response.content


@pytest.mark.django_db
def test_scan_query_redirects_existing_barcode(client, user, wine_factory):
    wine = wine_factory(user=user, barcode="123456789")
    client.force_login(user)
    response = client.get(reverse("wine-scan"), {"code": wine.barcode})
    assertRedirects(response, reverse("wine-detail", kwargs={"pk": wine.pk}))


@pytest.mark.django_db
def test_scan_query_preserves_unknown_qr_value(client, user):
    client.force_login(user)
    response = client.get(reverse("wine-scan"), {"code": "QR-WINE-42"})
    assertRedirects(
        response,
        f"{reverse('wine-add-choose')}?barcode=QR-WINE-42",
        fetch_redirect_response=False,
    )
