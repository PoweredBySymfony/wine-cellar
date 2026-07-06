from urllib.parse import urljoin

from allauth.account.adapter import DefaultAccountAdapter
from django.conf import settings
from django.urls import reverse


class ConfigurableSignupAccountAdapter(DefaultAccountAdapter):

    def is_open_for_signup(self, request):
        return getattr(settings, "ENABLE_SIGNUPS", False)

    def send_mail(self, template_prefix, email, context):
        context.setdefault("site_url", settings.SITE_URL.rstrip("/"))
        return super().send_mail(template_prefix, email, context)

    def get_email_confirmation_url(self, request, emailconfirmation):
        path = reverse(
            "account_confirm_email",
            kwargs={"key": emailconfirmation.key},
        )
        return urljoin(
            f"{settings.SITE_URL.rstrip('/')}/",
            path.lstrip("/"),
        )
