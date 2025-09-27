from django.test import TestCase
from django.contrib.auth import get_user_model, authenticate


class PhoneOrEmailBackendTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            email="alice@example.com",
            phone="1234567890",
            first_name="Alice",
        )
        self.user.set_password("StrongPass123!")
        self.user.is_active = True
        self.user.is_verified = True
        self.user.save()

    def test_authenticate_with_email(self):
        user = authenticate(email="alice@example.com", password="StrongPass123!")
        self.assertIsNotNone(user)
        self.assertEqual(user.pk, self.user.pk)

    def test_authenticate_with_phone(self):
        user = authenticate(phone="1234567890", password="StrongPass123!")
        self.assertIsNotNone(user)
        self.assertEqual(user.pk, self.user.pk)

    def test_authenticate_invalid_credentials(self):
        user = authenticate(email="alice@example.com", password="WrongPass")
        self.assertIsNone(user)
