import hashlib
from urllib.parse import urljoin

from allauth.account.models import EmailAddress
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.contrib.auth.decorators import login_not_required
from django.contrib.auth.tokens import default_token_generator
from django.core.cache import cache
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.utils import translation
from django.utils.decorators import method_decorator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import FormView, TemplateView, UpdateView

from wine_cellar.apps.user.forms import MagicLoginRequestForm, UserSettingsForm
from wine_cellar.apps.user.models import UserSettings
from wine_cellar.apps.user.signup_adapter import ConfigurableSignupAccountAdapter


@method_decorator(login_not_required, name="dispatch")
class MagicLoginRequestView(FormView):
    template_name = "account/login.html"
    form_class = MagicLoginRequestForm
    success_url = reverse_lazy("magic-login-sent")

    def form_valid(self, form):
        email = form.cleaned_data["email"].strip().lower()
        rate_key = f"magic-login:{hashlib.sha256(email.encode()).hexdigest()}"
        if cache.add(rate_key, 1, timeout=60):
            email_address = (
                EmailAddress.objects.select_related("user")
                .filter(email__iexact=email, verified=True, user__is_active=True)
                .first()
            )
            if email_address:
                user = email_address.user
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                token = default_token_generator.make_token(user)
                path = reverse(
                    "magic-login-confirm",
                    kwargs={"uidb64": uid, "token": token},
                )
                login_url = urljoin(
                    f"{settings.SITE_URL.rstrip('/')}/",
                    path.lstrip("/"),
                )
                ConfigurableSignupAccountAdapter(self.request).send_mail(
                    "account/email/magic_login",
                    email,
                    {
                        "user": user,
                        "login_url": login_url,
                        "site_url": settings.SITE_URL.rstrip("/"),
                    },
                )
        self.request.session["magic_login_email"] = email
        return super().form_valid(form)


@method_decorator(login_not_required, name="dispatch")
class MagicLoginSentView(TemplateView):
    template_name = "account/magic_login_sent.html"


@method_decorator(login_not_required, name="dispatch")
class MagicLoginConfirmView(View):
    def get(self, request, uidb64, token):
        user = self._get_user(uidb64)
        if (
            user
            and default_token_generator.check_token(user, token)
            and EmailAddress.objects.filter(
                user=user,
                verified=True,
            ).exists()
        ):
            login(
                request,
                user,
                backend="django.contrib.auth.backends.ModelBackend",
            )
            messages.success(request, _("You are now signed in."))
            return redirect(settings.LOGIN_REDIRECT_URL)
        messages.error(
            request,
            _("This sign-in link is invalid or has expired. Request a new one."),
        )
        return redirect("account_login")

    @staticmethod
    def _get_user(uidb64):
        try:
            user_id = urlsafe_base64_decode(uidb64).decode()
            return get_user_model().objects.get(pk=user_id, is_active=True)
        except (ValueError, TypeError, OverflowError, get_user_model().DoesNotExist):
            return None


class UserSettingsView(UpdateView):
    template_name = "settings.html"
    form_class = UserSettingsForm
    success_url = reverse_lazy("user-settings")

    def form_valid(self, form):
        response = super().form_valid(form)
        user_language = form.cleaned_data["language"]
        translation.activate(user_language)
        response.set_cookie(settings.LANGUAGE_COOKIE_NAME, user_language)
        return response

    def get_object(self, queryset=None):
        user = self.request.user
        return get_user_settings(user)


def get_user_settings(user):
    if not hasattr(user, "user_settings"):
        user.user_settings = UserSettings()
    return user.user_settings
