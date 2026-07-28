from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('conflict_reports', '0002_rainfallbaseline'),
    ]

    operations = [
        migrations.AddField(
            model_name='reportdatasnapshot',
            name='health_confirmed_cases',
            field=models.FloatField(blank=True, help_text='HDX sitrep — latest cumulative confirmed cases in window', null=True),
        ),
        migrations.AddField(
            model_name='reportdatasnapshot',
            name='health_suspected_cases',
            field=models.FloatField(blank=True, help_text='HDX sitrep — latest cumulative suspected cases in window', null=True),
        ),
        migrations.AddField(
            model_name='reportdatasnapshot',
            name='health_deaths',
            field=models.FloatField(blank=True, help_text='HDX sitrep — latest cumulative deaths in window', null=True),
        ),
        migrations.AddField(
            model_name='reportdatasnapshot',
            name='health_alert_score',
            field=models.FloatField(blank=True, help_text='Normalised 0-100 — informational only, NOT included in composite_score', null=True),
        ),
        migrations.AddField(
            model_name='reportdatasnapshot',
            name='health_data_as_of',
            field=models.DateField(blank=True, help_text='Reference date of the HDX figures used', null=True),
        ),
    ]
