from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.utils.timezone import now
from .forms import RegisterForm, LoginForm, UserProfileForm, ChangePasswordForm
from common.models import AuthUser, Userprofiles
from django.db import transaction
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password
from django.contrib import messages
from django.contrib.auth.decorators import login_required

def index(request):
    if request.session.get('user_id'):
        context = {'logged_in': True}
    else:
        context = {'logged_in': False}
    
    return render(request, 'shop/index.html', context)

def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            try:
                with transaction.atomic():
                    user = AuthUser.objects.create(
                        username=cd['username'],
                        password=make_password(cd['password']),
                        email=cd.get('email', ''),
                        first_name=cd.get('first_name', ''),
                        last_name=cd.get('last_name', ''),
                        is_active=True,
                        is_staff=False,
                        is_superuser=False,
                        date_joined=now(),
                    )

                    Userprofiles.objects.create(
                        authuser=user,
                        phone_number=cd.get('phone_number'),
                        base_delivery_adress=cd.get('base_delivery_adress'),
                        display_name=cd.get('display_name'),
                    )

                    messages.success(request, "Реєстрація успішна!")
                    return redirect("/login/")
            except Exception as e:
                messages.error(request, f"Помилка під час створення: {e}")
        else:
            messages.warning(request, "Будь ласка, виправте помилки у формі.")
    else:
        form = RegisterForm()

    return render(request, "shop/register.html", {"form": form})


def login(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            try:
                user = AuthUser.objects.get(username=username)
                if check_password(password, user.password):
                    request.session['user_id'] = user.id 
                    request.session['username'] = user.username
                    messages.success(request, "Вхід успішний!")
                    return redirect("/")
                else:
                    messages.error(request, "Неправильний пароль.")
            except AuthUser.DoesNotExist:
                messages.error(request, "Користувача не знайдено.")
    else:
        form = LoginForm()

    return render(request, "shop/login.html", {"form": form})


def logout(request):
    request.session.flush()
    return redirect("/")

@login_required
def profile(request):
    user_id = request.session.get('user_id')
    if user_id:
        user = AuthUser.objects.get(id=user_id)
        user_profile = Userprofiles.objects.get(authuser=user)
        return render(request, 'shop/profile.html', {'user_profile': user_profile})
    else:
        redirect('/login/')

@login_required
def profile(request):
    user_id = request.session.get('user_id')
    authuser = AuthUser.objects.get(id=user_id)
    profile = Userprofiles.objects.get(authuser=authuser)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile, authuser_instance=authuser)
        if form.is_valid():
            authuser.first_name = form.cleaned_data['first_name']
            authuser.last_name = form.cleaned_data['last_name']
            authuser.email = form.cleaned_data['email']
            authuser.username = form.cleaned_data['username']
            authuser.save()
            form.save()
            messages.success(request, 'Профіль успішно оновлено')
            return redirect('/profile/')
    else:
        form = UserProfileForm(instance=profile, authuser_instance=authuser)

    return render(request, 'shop/profile.html', {'form': form})

@login_required
def change_password(request):
    user_id = request.session.get('user_id')
    authuser = AuthUser.objects.get(id=user_id)

    if request.method == 'POST':
        form = ChangePasswordForm(request.POST, user=authuser)
        if form.is_valid():
            authuser.password = make_password(form.cleaned_data['new_password'])
            authuser.save()
            messages.success(request, 'Пароль успішно змінено')
            return redirect('/profile/')
    else:
        form = ChangePasswordForm(user=authuser)

    return render(request, 'shop/change_password.html', {'form': form})