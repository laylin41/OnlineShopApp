from django.test import TestCase
from django.urls import reverse
from common.models import AuthUser, Userprofiles
from django.contrib.messages import get_messages
from django.utils.timezone import now
from django.contrib.auth.hashers import check_password


class TestRegisterLoginProfile(TestCase):
    def setUp(self):
        # Створимо користувача для тестів логіну і профілю
        self.user = AuthUser.objects.create(
            username="existinguser",
            password="pbkdf2_sha256$260000$fake$hashedpassword",
            email="exist@example.com",
            first_name="Exist",
            last_name="User",
            is_active=True,
            date_joined=now(),
            is_superuser=False,
            is_staff=False,
        )
        self.userprofiles = Userprofiles.objects.create(
            authuser=self.user,
            phone_number="1234567890",
            base_delivery_adress="Some address",
            display_name="Existing User"
        )

    def test_register_get(self):
        # GET запит повертає форму реєстрації
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)

    def test_register_post_success(self):
        data = {
            'username': 'newuser',
            'password': 'StrongPass123!',
            'confirm_password': 'StrongPass123!',
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'phone_number': '0987654321',
            'base_delivery_adress': 'New Address',
            'display_name': 'Newbie'
        }
        response = self.client.post(reverse('register'), data)
        self.assertRedirects(response, '/login/')
        self.assertTrue(AuthUser.objects.filter(username='newuser').exists())

    def test_register_post_invalid(self):
        # Наприклад, password2 не співпадає з password (якщо в формі є підтвердження)
        data = {
            'username': 'baduser',
            'password': 'pass1',
            'password2': 'pass2',
        }
        response = self.client.post(reverse('register'), data)
        self.assertEqual(response.status_code, 200)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("Будь ласка" in str(m) for m in messages))
        self.assertFalse(AuthUser.objects.filter(username='baduser').exists())

    def test_login_get(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)

    def test_login_post_success(self):
        # Спочатку треба зберегти правильний хеш пароля
        self.user.password = 'pbkdf2_sha256$260000$fake$hashedpassword'
        self.user.set_password('CorrectPass123')
        self.user.save()

        data = {
            'username': 'existinguser',
            'password': 'CorrectPass123',
        }
        profile = self.user.userprofiles_set.first()
        response = self.client.post(reverse('login'), data)
        self.assertRedirects(response, '/')
        session = self.client.session
        self.assertEqual(session['user_id'], self.user.id)
        self.assertEqual(session['username'], self.user.username)
        self.assertEqual(session['user_profile_id'], profile.profile_id if profile else None)

    def test_login_post_wrong_password(self):
        data = {
            'username': 'existinguser',
            'password': 'WrongPass',
        }
        response = self.client.post(reverse('login'), data)
        self.assertEqual(response.status_code, 200)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("Неправильний пароль" in str(m) for m in messages))

    def test_login_post_user_not_found(self):
        data = {
            'username': 'nonexistent',
            'password': 'any',
        }
        response = self.client.post(reverse('login'), data)
        self.assertEqual(response.status_code, 200)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("Користувача не знайдено" in str(m) for m in messages))

    def test_profile_get_authenticated(self):
        # Залогінимо користувача через сесію
        session = self.client.session
        session['user_id'] = self.user.id
        session.save()

        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
        self.assertTrue(response.context['logged_in'])

    def test_profile_post_update(self):
        session = self.client.session
        session['user_id'] = self.user.id
        session.save()

        profile = self.user.userprofiles_set.first()

        data = {
            'first_name': 'UpdatedFirst',
            'last_name': 'UpdatedLast',
            'email': 'updated@example.com',
            'username': 'existinguser',  # username не міняємо
            'phone_number': profile.phone_number if profile else '',
            'base_delivery_adress': profile.base_delivery_adress if profile else '',
            'display_name': profile.display_name if profile else '',
        }
        response = self.client.post(reverse('profile'), data)
        self.assertRedirects(response, '/profile/')

        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'UpdatedFirst')
        self.assertEqual(self.user.email, 'updated@example.com')

    def test_profile_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('profile'))
        self.assertRedirects(response, '/login/')