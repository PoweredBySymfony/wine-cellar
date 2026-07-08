from allauth.account.models import EmailAddress
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.contrib.auth.decorators import login_not_required
from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils import translation
from django.utils.decorators import method_decorator
from django.utils.http import urlsafe_base64_decode
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import FormView, TemplateView, UpdateView

from wine_cellar.apps.user.forms import EmailPasswordLoginForm, UserSettingsForm
from wine_cellar.apps.user.models import UserSettings


@method_decorator(login_not_required, name="dispatch")
class MagicLoginRequestView(FormView):
    template_name = "account/login.html"
    form_class = EmailPasswordLoginForm
    success_url = reverse_lazy("homepage")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs

    def form_valid(self, form):
        login(
            self.request,
            form.user,
            backend="django.contrib.auth.backends.ModelBackend",
        )
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
