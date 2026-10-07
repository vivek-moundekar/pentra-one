from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

from .models import EducationProfile


class EducationRegistrationForm(UserCreationForm):

    first_name = forms.CharField(
        max_length=150,
        required=True,
        label="Full Name",
        widget=forms.TextInput(
            attrs={
                "placeholder": "Enter your full name",
                "class": "form-control",
            }
        ),
    )

    username = forms.CharField(
        max_length=150,
        required=True,
        label="Username",
        widget=forms.TextInput(
            attrs={
                "placeholder": "Choose a username",
                "class": "form-control",
            }
        ),
    )

    email = forms.EmailField(
        required=True,
        label="Email",
        widget=forms.EmailInput(
            attrs={
                "placeholder": "Enter your email",
                "class": "form-control",
            }
        ),
    )

    password1 = forms.CharField(
        required=True,
        label="Password",
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Enter your password",
                "class": "form-control",
            }
        ),
    )

    password2 = forms.CharField(
        required=True,
        label="Confirm Password",
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Confirm your password",
                "class": "form-control",
            }
        ),
    )

    role = forms.ChoiceField(
        choices=EducationProfile.ROLE_CHOICES,
        required=True,
        label="I am a",
        widget=forms.RadioSelect,
    )

    class Meta:
        model = User

        fields = [
            "first_name",
            "username",
            "email",
            "password1",
            "password2",
            "role",
        ]

    def save(self, commit=True):

        user = super().save(commit=False)

        user.first_name = self.cleaned_data["first_name"]
        user.email = self.cleaned_data["email"]

        if commit:
            user.save()

            EducationProfile.objects.create(
                user=user,
                role=self.cleaned_data["role"],
            )

        return user