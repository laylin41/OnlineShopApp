from django import forms
from common.models import AuthUser, Userprofiles
from django.utils import timezone

class RegisterForm(forms.Form):
    username = forms.CharField(label="Ім’я користувача", max_length=150, required=True)
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput, required=True)
    confirm_password = forms.CharField(label="Підтвердження паролю", widget=forms.PasswordInput, required=True)

    first_name = forms.CharField(label="Ім'я", max_length=150, required=False)
    last_name = forms.CharField(label="Прізвище", max_length=150, required=False)
    email = forms.EmailField(label="Електронна пошта", required=False)
    phone_number = forms.CharField(label="Номер телефону", max_length=15, required=False)
    base_delivery_adress = forms.CharField(label="Базова адреса доставки", max_length=255, required=False)
    display_name = forms.CharField(label="Відображуване ім'я", max_length=150, required=False)

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm = cleaned_data.get("confirm_password")

        if not (password and confirm):
            raise forms.ValidationError("Будь ласка введіть пароль та його підтвердження.")
        elif password != confirm:
            raise forms.ValidationError("Паролі не співпадають.")
        
        return cleaned_data

class LoginForm(forms.Form):
    username = forms.CharField(label="Ім’я користувача", max_length=150)
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput)
