from http import HTTPStatus

import pytest
from django.test import override_settings
from django.urls import reverse
from pytest_django.asserts import assertContains, assertRedirects, assertTemplateUsed


@pytest.mark.django_db
def test_user_settings_page(client, user):
    client.force_login(user)
    r = client.get(reverse("user-settings"))
    assert r.status_code == HTTPStatus.OK
    assertTemplateUsed(response=r, template_name="base.html")
    assertTemplateUsed(response=r, template_name="settings.html")

    data = {
        "language": "de-DE",
        "currency": "EUR",
        "notifications": True,
    }
    r = client.post(reverse("user-settings"), data, follow=True)
    assert r.status_code == HTTPStatus.OK
    assertRedirects(response=r, expected_url=reverse("user-settings"))
    user_settings = user.user_settings
    assert user_settings.language == "de-DE"
    assert user_settings.currency == "EUR"
    assert user_settings.notifications

    data = {
        "language": "en-gb",
        "currency": "EUR",
        "notifications": False,
    }
    r = client.post(reverse("user-settings"), data, follow=True)
    assert r.status_code == HTTPStatus.OK
    user_settings.refresh_from_db()
    assert user_settings.language == "en-gb"
    assert user_settings.currency == "EUR"
    assert not user_settings.notifications


@pytest.mark.django_db
def test_user_signup_disabled(client, user):
    r = client.get(reverse("account_signup"))
    assert r.status_code == HTTPStatus.OK
    assertTemplateUsed(response=r, template_name="base.html")
    assertTemplateUsed(response=r, template_name="account/signup_closed.html")


@override_settings(ENABLE_SIGNUPS=True)
@pytest.mark.django_db
def test_user_signup_enabled(client, user):
    r = client.get(reverse("account_signup"))
    assert r.status_code == HTTPStatus.OK
    assertTemplateUsed(response=r, template_name="base.html")
    assertTemplateUsed(response=r, template_name="account/signup.html")


@pytest.mark.django_db
def test_header_language_switches_to_french(client, user):
    client.force_login(user)

    response = client.post(
        reverse("set_language"),
        {"language": "fr-FR", "next": reverse("homepage")},
        follow=True,
    )

    assert response.status_code == HTTPStatus.OK
    assertContains(response, "Collection personnelle")
    assertContains(response, "Ma cave à vin,")
    assertContains(response, "Langue actuelle")


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("language", "expected"),
    [
        ("fr-FR", ("Ma sélection", "Filtres", "Type de vin", "Allemagne")),
        ("de-DE", ("Meine Auswahl", "Filter", "Weinart", "Frankreich")),
        ("en-gb", ("My selection", "Filters", "Wine Type")),
    ],
)
def test_wine_list_is_translated_for_every_supported_language(
    client, user, language, expected
):
    client.force_login(user)
    client.post(
        reverse("set_language"),
        {"language": language, "next": reverse("wine-list")},
    )

    response = client.get(reverse("wine-list"))

    for text in expected:
        assertContains(response, text)
