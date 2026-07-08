from allauth.account.models import EmailAddress
from django import forms
from django.contrib.auth import authenticate, get_user_model
from django.forms import ModelForm
from django.utils.translation import gettext_lazy as _

from wine_cellar.apps.user.models import UserSettings


class EmailPasswordLoginForm(forms.Form):
    email = forms.EmailField(
        label=_("Email"),
        widget=forms.EmailInput(
            attrs={
                "autocomplete": "email",
                "placeholder": _("you@example.com"),
            }
        ),
    )
    password = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "autocomplete": "current-password",
                "placeholder": _("Your password"),
            }
        ),
    )

    error_messages = {
        "invalid_login": _(
            "Enter a valid email address and password. "
            "Both fields may be case-sensitive."
        ),
        "inactive": _("This account is inactive."),
        "unverified": _("Confirm your email address before signing in."),
    }

    def __init__(self, *args, request=None, **kwargs):
        self.request = request
        self.user = None
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email", "").strip().lower()
        password = cleaned_data.get("password")

        if email and password:
            email_address = (
                EmailAddress.objects.select_related("user")
                .filter(email__iexact=email)
                .first()
            )
            user = (
                email_address.user
                if email_address
                else get_user_model().objects.filter(email__iexact=email).first()
            )
            username = user.get_username() if user else email
            self.user = authenticate(
                self.request,
                username=username,
                password=password,
            )
            if self.user is None:
                raise forms.ValidationError(
                    self.error_messages["invalid_login"],
                    code="invalid_login",
                )
            if not self.user.is_active:
                raise forms.ValidationError(
                    self.error_messages["inactive"],
                    code="inactive",
                )
            if email_address and not email_address.verified:
                raise forms.ValidationError(
                    self.error_messages["unverified"],
                    code="unverified",
                )
        return cleaned_data


class UserSettingsForm(ModelForm):

    class Meta:
        model = UserSettings
        fields = ["language", "currency", "notifications"]
        labels = {
            "language": _("Language"),
            "currency": _("Currency"),
            "notifications": _("Email Notifications"),
        }
        help_texts = {
            "language": _("The language the site is displayed in."),
            "currency": _("The default currency used for the price of a wine."),
            "notifications": _("Receive email notifications."),
        }
