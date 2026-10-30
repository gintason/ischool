"""App-store review login and one-time use of verified codes."""
from unittest import mock

from django.core.cache import cache
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from .models import VerificationCode

SEND = '/api/users/phone/send-code/'
VERIFY = '/api/users/phone/verify-code/'
LOGIN = '/api/users/phone/login/'


@override_settings(
    REVIEW_LOGIN_IDENTIFIERS=['PlayReview@ischool.ng', '08000000001'],
    REVIEW_LOGIN_CODE='246810',
)
class ReviewLoginTests(TestCase):
    def setUp(self):
        cache.clear()  # OTP endpoints are throttled per IP
        self.client = APIClient()

    def login(self, identifier, method):
        with mock.patch('users.sms_services.send_email_code') as email, \
                mock.patch('users.sms_services.send_sms_auto_fallback') as sms:
            res = self.client.post(SEND, {'identifier': identifier, 'method': method}, format='json')
            self.assertEqual(res.status_code, 200, res.data)
            self.assertNotIn('code', res.data)
            email.assert_not_called()
            sms.assert_not_called()
        res = self.client.post(VERIFY, {'identifier': identifier, 'method': method, 'code': '246810'}, format='json')
        self.assertEqual(res.status_code, 200, res.data)
        res = self.client.post(LOGIN, {'identifier': identifier, 'method': method, 'platform': 'ola'}, format='json')
        self.assertEqual(res.status_code, 200, res.data)
        self.assertIn('access', res.data['tokens'])
        return res

    def test_email_reviewer_logs_in_with_fixed_code(self):
        res = self.login('playreview@ischool.ng', 'email')
        self.assertEqual(res.data['user']['email'], 'playreview@ischool.ng')

    def test_code_is_reusable_across_logins(self):
        first = self.login('playreview@ischool.ng', 'email')
        second = self.login('playreview@ischool.ng', 'email')
        self.assertEqual(first.data['user']['id'], second.data['user']['id'])

    def test_phone_reviewer_any_format(self):
        from django.contrib.auth import get_user_model
        get_user_model().objects.create(
            username='reviewer_phone', email='reviewer-phone@ischool.ng', phone_number='2348000000001')
        res = self.login('+2348000000001', 'phone')
        self.assertEqual(res.data['user']['phone_number'], '2348000000001')

    def test_wrong_code_rejected(self):
        self.client.post(SEND, {'identifier': 'playreview@ischool.ng', 'method': 'email'}, format='json')
        res = self.client.post(VERIFY, {'identifier': 'playreview@ischool.ng', 'method': 'email', 'code': '111111'}, format='json')
        self.assertEqual(res.status_code, 400)

    def test_normal_users_still_get_random_code_by_email(self):
        with mock.patch('users.sms_services.send_email_code', return_value=True) as email:
            res = self.client.post(SEND, {'identifier': 'someone@example.com', 'method': 'email'}, format='json')
        self.assertEqual(res.status_code, 200)
        email.assert_called_once()
        self.assertEqual(email.call_args.args[1], VerificationCode.objects.get(identifier='someone@example.com').code)

    @override_settings(REVIEW_LOGIN_CODE='')
    def test_bypass_off_without_code(self):
        with mock.patch('users.sms_services.send_email_code', return_value=True) as email:
            self.client.post(SEND, {'identifier': 'playreview@ischool.ng', 'method': 'email'}, format='json')
        email.assert_called_once()


class VerifiedCodeIsSingleUseTests(TestCase):
    def setUp(self):
        cache.clear()  # OTP endpoints are throttled per IP
        self.client = APIClient()

    def test_login_consumes_verification(self):
        VerificationCode.objects.create(identifier='a@b.com', method='email', is_verified=True)
        payload = {'identifier': 'a@b.com', 'method': 'email', 'platform': 'ola'}
        self.assertEqual(self.client.post(LOGIN, payload, format='json').status_code, 200)
        self.assertEqual(self.client.post(LOGIN, payload, format='json').status_code, 400)

    def test_old_verification_rejected(self):
        from django.utils import timezone
        VerificationCode.objects.create(
            identifier='a@b.com', method='email', is_verified=True,
            expires_at=timezone.now() - timezone.timedelta(minutes=1))
        res = self.client.post(LOGIN, {'identifier': 'a@b.com', 'method': 'email'}, format='json')
        self.assertEqual(res.status_code, 400)
