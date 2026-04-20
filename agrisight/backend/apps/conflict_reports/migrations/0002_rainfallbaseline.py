import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('conflict_reports', '0001_initial'),
        ('geospatial', '0003_region_acled_name_aliases'),
    ]

    operations = [
        migrations.CreateModel(
            name='RainfallBaseline',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('month', models.PositiveSmallIntegerField(help_text='Calendar month 1-12')),
                ('mean_mm', models.FloatField()),
                ('std_mm', models.FloatField(default=0.0)),
                ('baseline_years', models.PositiveSmallIntegerField(default=10)),
                ('computed_at', models.DateTimeField(auto_now=True)),
                ('region', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='rainfall_baselines',
                    to='geospatial.region',
                )),
            ],
            options={
                'unique_together': {('region', 'month')},
            },
        ),
    ]
