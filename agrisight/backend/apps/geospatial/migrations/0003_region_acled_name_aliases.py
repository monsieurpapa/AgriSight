from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('geospatial', '0002_alter_regionaccess_access_level_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='region',
            name='acled_name_aliases',
            field=models.JSONField(blank=True, default=list, help_text='ACLED district name variants for crosswalk'),
        ),
    ]
