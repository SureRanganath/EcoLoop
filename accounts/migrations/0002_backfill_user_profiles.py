from django.db import migrations


def backfill_profiles(apps, schema_editor):
    """Create a default UserProfile for every user that lacks one.

    Users created through the Django admin before the ensure_user_profile
    signal existed (e.g. the 'admin' account) had no profile, which made
    user.profile lookups fail in views and templates.
    """
    User = apps.get_model('auth', 'User')
    UserProfile = apps.get_model('accounts', 'UserProfile')

    for user in User.objects.filter(profile__isnull=True).iterator():
        full_name = f"{user.first_name} {user.last_name}".strip()
        UserProfile.objects.create(
            user=user,
            role='buyer',
            company_name=full_name or user.username,
            industry_type='Other',
            city='',
            state='',
        )


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.RunPython(backfill_profiles, migrations.RunPython.noop),
    ]
