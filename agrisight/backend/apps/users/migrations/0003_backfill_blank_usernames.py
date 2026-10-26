"""
Give users created through e-mail sign-up a real username.

Before the adapter fix, allauth saved e-mail sign-ups with username=''. Only
one such row can exist (username is unique), but it should still get a proper
value so it can't collide with anything later.
"""
from django.db import migrations
from django.utils.crypto import get_random_string
from django.utils.text import slugify


def backfill(apps, schema_editor):
    User = apps.get_model('users', 'User')
    for user in User.objects.filter(username=''):
        base = slugify((user.email or '').split('@')[0]).replace('-', '_')[:140] or 'user'
        candidate = base
        while User.objects.filter(username__iexact=candidate).exists():
            candidate = f"{base}_{get_random_string(6, 'abcdefghijklmnopqrstuvwxyz0123456789')}"
        User.objects.filter(pk=user.pk).update(username=candidate)


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_user_deleted_at_historicaluser'),
    ]

    operations = [
        migrations.RunPython(backfill, migrations.RunPython.noop),
    ]
