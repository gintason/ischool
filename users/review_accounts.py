"""
App-store review accounts (created by `manage.py create_review_accounts`).

They must never be auto-matched with real users: real students must not be
put in the review teacher's classes, and the review student must not appear
in real teachers' classes.
"""
REVIEW_ACCOUNT_EMAILS = (
    'ola.review@ischool.ng',
    'ole.review@ischool.ng',
    'teacher.review@ischool.ng',
)


def is_review_account(user):
    return bool(user) and (getattr(user, 'email', '') or '').lower() in REVIEW_ACCOUNT_EMAILS


def without_review_accounts(queryset):
    return queryset.exclude(email__in=REVIEW_ACCOUNT_EMAILS)
