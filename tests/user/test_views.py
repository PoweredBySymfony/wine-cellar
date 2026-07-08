from http import HTTPStatus

import pytest
from allauth.account.models import EmailAddress
from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.test import override_settings
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
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
    assertContains(r, "Create your cellar.")
    assertContains(r, 'type="password"', count=2)
    assertContains(r, "data-password-toggle", count=2)


@override_settings(ENABLE_SIGNUPS=True, SITE_URL="http://testserver")
@pytest.mark.django_db
def test_signup_sends_branded_verification_email(client):
    response = client.post(
        reverse("account_signup"),
        {
            "email": "new-cellar@example.com",
            "password1": "A-strong-cellar-password-2026",
            "password2": "A-strong-cellar-password-2026",
        },
    )

    assertRedirects(response, reverse("account_email_verification_sent"))
    assert len(mail.outbox) == 1
    message = mail.outbox[0]
    assert message.subject == "Activez votre compte Wine Cellar"
    assert "accounts/confirm-email/" in message.body
    assert message.alternatives
    html = message.alternatives[0].content
    assert "Vérifier mon adresse" in html
    assert "static/images/favicon.svg" in html


@override_settings(
    ENABLE_SIGNUPS=True,
    SITE_URL="http://testserver",
    ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION=True,
)
@pytest.mark.django_db
def test_signup_email_confirmation_logs_user_in(client):
    client.post(
        reverse("account_signup"),
        {
            "email": "instant-cellar@example.com",
            "password1": "A-strong-cellar-password-2026",
            "password2": "A-strong-cellar-password-2026",
        },
    )
    confirmation_url = next(
        line.strip()
        for line in mail.outbox[0].body.splitlines()
        if "accounts/confirm-email/" in line
    )

    response = client.post(confirmation_url)

    assertRedirects(response, reverse("homepage"), fetch_redirect_response=False)
    assert "_auth_user_id" in client.session
    assert EmailAddress.objects.get(email="instant-cellar@example.com").verified


@pytest.mark.django_db
def test_login_uses_email_and_password_visibility_markup(client):
    response = client.get(reverse("account_login"))

    assert response.status_code == HTTPStatus.OK
    assertContains(response, "Welcome back.")
    assertContains(response, 'type="email"')
    assertContains(response, 'type="password"')
    assertContains(response, "data-password-toggle")
    assertContains(response, "Sign in")
    assert b"Email me a secure sign-in link" not in response.content


@pytest.mark.django_db
def test_login_accepts_verified_email_and_password(client, user):
    EmailAddress.objects.create(
        user=user,
        email=user.email,
        verified=True,
        primary=True,
    )

    response = client.post(
        reverse("account_login"),
        {"email": user.email, "password": "password"},
    )

    assertRedirects(response, reverse("homepage"), fetch_redirect_response=False)
    assert "_auth_user_id" in client.session
    assert mail.outbox == []


@pytest.mark.django_db
def test_login_rejects_wrong_password_without_sending_email(client, user):
    EmailAddress.objects.create(
        user=user,
        email=user.email,
        verified=True,
        primary=True,
    )

    response = client.post(
        reverse("account_login"),
        {"email": user.email, "password": "wrong-password"},
    )

    assert response.status_code == HTTPStatus.OK
    assert "_auth_user_id" not in client.session
    assert mail.outbox == []


@pytest.mark.django_db
def test_login_rejects_unverified_email(client, user):
    EmailAddress.objects.create(user=user, email=user.email, verified=False)

    response = client.post(
        reverse("account_login"),
        {"email": user.email, "password": "password"},
    )

    assert response.status_code == HTTPStatus.OK
    assert "_auth_user_id" not in client.session
    assert mail.outbox == []


@pytest.mark.django_db
def test_invalid_magic_login_link_is_rejected(client, user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)

    response = client.get(
        reverse(
            "magic-login-confirm",
            kwargs={"uidb64": uid, "token": f"{token}invalid"},
        )
    )

    assertRedirects(response, reverse("account_login"))
    assert "_auth_user_id" not in client.session


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
