import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('geospatial', '0003_region_acled_name_aliases'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ConflictReport',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('district_ids', models.JSONField(help_text='List of Region PKs included in this report')),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('status', models.CharField(choices=[('PENDING', 'Pending'), ('PROCESSING', 'Processing'), ('COMPLETE', 'Complete'), ('FAILED', 'Failed')], default='PENDING', max_length=20)),
                ('celery_task_id', models.CharField(blank=True, max_length=255)),
                ('pdf_file', models.FileField(blank=True, null=True, upload_to='conflict_reports/')),
                ('recipient_email', models.EmailField(blank=True, max_length=254)),
                ('email_status', models.CharField(choices=[('PENDING', 'Pending'), ('SENT', 'Sent'), ('FAILED', 'Failed'), ('NOT_REQUESTED', 'Not Requested')], default='NOT_REQUESTED', max_length=20)),
                ('error_message', models.TextField(blank=True)),
                ('feedback_token', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='conflict_reports', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='NDVIBaseline',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mean_ndvi', models.FloatField()),
                ('std_ndvi', models.FloatField()),
                ('baseline_years', models.PositiveSmallIntegerField(default=3)),
                ('computed_at', models.DateTimeField(auto_now=True)),
                ('region', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='ndvi_baseline', to='geospatial.region')),
            ],
        ),
        migrations.CreateModel(
            name='ReportDataSnapshot',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ndvi_current', models.FloatField(blank=True, null=True)),
                ('ndvi_baseline_mean', models.FloatField(blank=True, null=True)),
                ('ndvi_anomaly', models.FloatField(blank=True, help_text='(current - baseline) / baseline * 100', null=True)),
                ('conflict_event_count', models.PositiveIntegerField(blank=True, null=True)),
                ('conflict_density_score', models.FloatField(blank=True, help_text='Normalised 0-100', null=True)),
                ('idp_count', models.PositiveIntegerField(blank=True, null=True)),
                ('displacement_score', models.FloatField(blank=True, help_text='Normalised 0-100', null=True)),
                ('rainfall_mm', models.FloatField(blank=True, null=True)),
                ('rainfall_deviation_pct', models.FloatField(blank=True, null=True)),
                ('rainfall_score', models.FloatField(blank=True, help_text='Normalised 0-100', null=True)),
                ('composite_score', models.FloatField(blank=True, help_text='Weighted 0-100 composite risk score', null=True)),
                ('ipc_phase_proxy', models.CharField(blank=True, max_length=30)),
                ('data_warnings', models.JSONField(default=list, help_text='List of data-quality warning strings')),
                ('signals_detail', models.JSONField(default=dict, help_text='Raw API response snippets for audit')),
                ('region', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='report_snapshots', to='geospatial.region')),
                ('report', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='snapshots', to='conflict_reports.conflictreport')),
            ],
            options={
                'unique_together': {('report', 'region')},
            },
        ),
        migrations.CreateModel(
            name='ReportFeedback',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('accuracy_rating', models.PositiveSmallIntegerField(blank=True, help_text='1 (poor) to 5 (excellent)', null=True)),
                ('missing_data', models.TextField(blank=True)),
                ('would_use_again', models.BooleanField(blank=True, null=True)),
                ('submitted_at', models.DateTimeField(auto_now=True)),
                ('report', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='feedback', to='conflict_reports.conflictreport')),
            ],
        ),
        migrations.AddIndex(
            model_name='conflictreport',
            index=models.Index(fields=['user', 'status'], name='cr_user_status_idx'),
        ),
        migrations.AddIndex(
            model_name='conflictreport',
            index=models.Index(fields=['feedback_token'], name='cr_feedback_token_idx'),
        ),
    ]
