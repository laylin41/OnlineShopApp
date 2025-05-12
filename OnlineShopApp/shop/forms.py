from django import forms
from common.models import AuthUser, Userprofiles, Reviews
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

class UserProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=150, required=False)
    last_name = forms.CharField(max_length=150, required=False)
    email = forms.EmailField(required=False)
    username = forms.CharField(max_length=150, required=False)

    class Meta:
        model = Userprofiles
        fields = ['phone_number', 'base_delivery_adress', 'display_name']

    def __init__(self, *args, **kwargs):
        authuser_instance = kwargs.pop('authuser_instance', None)
        super().__init__(*args, **kwargs)

        self.fields['display_name'].required = True
        if authuser_instance:
            self.fields['first_name'].initial = authuser_instance.first_name
            self.fields['last_name'].initial = authuser_instance.last_name
            self.fields['email'].initial = authuser_instance.email
            self.fields['username'].initial = authuser_instance.username

from django.contrib.auth.hashers import check_password

class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(widget=forms.PasswordInput, label='Старий пароль')
    new_password = forms.CharField(widget=forms.PasswordInput, label='Новий пароль')
    confirm_password = forms.CharField(widget=forms.PasswordInput, label='Підтвердіть пароль')

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        if not check_password(cleaned_data.get('old_password'), self.user.password):
            self.add_error('old_password', 'Неправильний старий пароль')
        if cleaned_data.get('new_password') != cleaned_data.get('confirm_password'):
            self.add_error('confirm_password', 'Паролі не співпадають')
        return cleaned_data

class ReviewForm(forms.ModelForm):
    RATING_CHOICES = [(i, i) for i in range(1, 6)]

    rating = forms.ChoiceField(choices=RATING_CHOICES, widget=forms.Select(), label="Оцінка")

    class Meta:
        model = Reviews
        fields = ['rating', 'comment']
        labels = {
            'comment': 'Коментар'
        }

