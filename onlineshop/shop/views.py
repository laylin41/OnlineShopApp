from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.utils.timezone import now

from shop.forms import ReviewForm
from .forms import RegisterForm, LoginForm, UserProfileForm, ChangePasswordForm, CheckoutForm
from common.models import AuthUser, Userprofiles, Goods, Reviews, Categories, Ordergood, Orders
from django.db import transaction
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import random, string


def index(request):
    goods = Goods.objects.filter(quantity__gt=0)
    context = {
        'logged_in': bool(request.session.get('user_id')),
        'goods': goods
    }
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
                    #start
                    # Знаходимо профіль користувача та зберігаємо його ID у сесію.
                    # Це потрібно для створення, редагування та видалення відгуків.
                    try:
                        user_profile = Userprofiles.objects.get(authuser=user)
                        request.session['user_profile_id'] = user_profile.profile_id
                    except Userprofiles.DoesNotExist:
                        request.session['user_profile_id'] = None
                    #end
                    messages.success(request, "Вхід успішний!")
                    return redirect("/")
                else:
                    messages.error(request, "Неправильний пароль.")
            except AuthUser.DoesNotExist:
                messages.error(request, "Користувача не знайдено.")
        else:
            messages.error(request, "Помилка у формі.")
    else:
        form = LoginForm()

    return render(request, "shop/login.html", {"form": form})


def logout(request):
    request.session.flush()
    return redirect("/")

def profile(request):
    user_id = request.session.get('user_id')
    if user_id:
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

        return render(request, 'shop/profile.html', {'form': form, 'logged_in': True})
    else:
        return redirect('/login/')
    
def change_password(request):
    user_id = request.session.get('user_id')
    if user_id:
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

        return render(request, 'shop/change_password.html', {'form': form, 'logged_in': True})
    else:
        return redirect('/login/')

from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from common.models import Goods, Reviews, Userprofiles
from .forms import ReviewForm

def goods_detail(request, good_id):
    good = get_object_or_404(Goods, pk=good_id)
    reviews = Reviews.objects.filter(good=good)
    user_profile_id = request.session.get('user_profile_id')

    # Окремі форми для створення та редагування
    review_form = ReviewForm()
    edit_form = None
    editing_review = None

    # Якщо є ?edit=... в URL — підготуємо edit_form
    edit_review_id = request.GET.get('edit')
    if edit_review_id and user_profile_id:
        try:
            editing_review = Reviews.objects.get(
                pk=edit_review_id,
                userprofile_id=user_profile_id,
                good=good
            )
            edit_form = ReviewForm(instance=editing_review)
        except Reviews.DoesNotExist:
            editing_review = None

    from django.http import HttpResponseRedirect

    # Обробка POST-запиту — або редагування, або новий відгук
    if request.method == 'POST' and user_profile_id:
        review_id = request.POST.get('review_id')
        if review_id:  # редагування
            review = get_object_or_404(
                Reviews,
                pk=review_id,
                userprofile_id=user_profile_id,
                good=good
            )
            edit_form = ReviewForm(request.POST, instance=review)
            if edit_form.is_valid():
                updated = edit_form.save(commit=False)
                updated.good = good
                updated.userprofile_id = user_profile_id
                updated.save()
                return HttpResponseRedirect(f"{request.path}#review-{updated.review_id}")

        else:  # створення нового
            review_form = ReviewForm(request.POST)
            if review_form.is_valid():
                new = review_form.save(commit=False)
                new.good = good
                new.userprofile_id = user_profile_id
                new.save()
                return redirect('goods-detail', good_id=good.good_id)

    return render(request, 'shop/goods_detail.html', {
        'good': good,
        'reviews': reviews,
        'review_form': review_form,
        'edit_form': edit_form,
        'editing_review': editing_review,
        'user_profile_id': user_profile_id,
    })


def delete_review(request, review_id):
    user_profile_id = request.session.get('user_profile_id')
    if not user_profile_id:
        return redirect('login')

    review = get_object_or_404(Reviews, pk=review_id)
    if review.userprofile.profile_id != user_profile_id:
        return HttpResponse("Недостатньо прав", status=403)

    good_id = review.good.good_id
    review.delete()
    return redirect('goods-detail', good_id=good_id)


def category_show(request, category_id):
    category = get_object_or_404(Categories, category_id=category_id)

    goods = Goods.objects.filter(category=category)

    return render(request, 'shop/category_detail.html', {
        'category': category,
        'goods': goods,
    })

def all_categories_show(request):
    return render(request, 'shop/categories.html')


def add_to_cart(request, good_id):
    good = get_object_or_404(Goods, good_id=good_id)
    cart = request.session.get('cart', [])

    if good.good_id in cart:
        messages.error(request, 'Товар вже в кошику!')
    else:
        cart.append(good.good_id)
        request.session['cart'] = cart
        request.session['cart_count'] = len(cart)
        request.session.modified = True

    return redirect('cart_view')

def cart_view(request):
    cart = request.session.get('cart', [])
    cart_items = []
    total_price = 0

    for good_id in cart:
        good = get_object_or_404(Goods, good_id=good_id)
        cart_items.append({
            'good_id': good.good_id,
            'name': good.name,
            'price': good.discounted_price,
        })
        total_price += good.discounted_price

    form = CheckoutForm()

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid() and cart_items:
            delivery_code = ''.join(random.choices(string.digits, k=14))
            user_id = request.session.get('user_profile_id')
            order = Orders.objects.create(
                delivery_adress_custom=form.cleaned_data['address'],
                delivery_code=delivery_code,
                status='Очікує продавця',
                userprofile_id=user_id
            )

            for item in cart:
                good = get_object_or_404(Goods, good_id=int(item))
                ordergood = Ordergood.objects.create(
                    order=order,
                    good=good,
                )
                ordergood.save()

            request.session['cart'] = []
            request.session['cart_count'] = 0
            request.session.modified = True

            order.save()
            return redirect('orders_history')

    context = {
        'cart_items': cart_items,
        'total_price': total_price,
        'form': form
    }
    return render(request, 'shop/cart.html', context)

def remove_from_cart(request, good_id):
    cart = request.session.get('cart', [])
    if good_id in cart:
        cart.remove(good_id)
        request.session['cart'] = cart
        request.session['cart_count'] = len(cart)
        request.session.modified = True
    return redirect('cart_view')

def checkout(request):
    return redirect('cart_view')


def orders_history(request):
    orders = Orders.objects.filter(userprofile_id=request.session.get('user_profile_id')).order_by('-order_id')

    orders_with_items = []
    for order in orders:
        items = Ordergood.objects.filter(order=order)
        total_price = 0
        for item in items:
            total_price += item.good.discounted_price
        orders_with_items.append({
            'order': order,
            'items': items,
            'total_price': total_price,
        })

    context = {
        'orders_with_items': orders_with_items,
    }
    return render(request, 'shop/orders_history.html', context)
