"""Seed QA users + a small DRC demo dataset for manual testing.
Run inside the backend container:
    docker compose exec -T backend python manage.py shell < scripts/qa_seed_demo.py
Creates admin@agrisight.test / field@agrisight.test (password AgriTest#2026), both email-verified.
"""
import datetime as dt
from django.contrib.gis.geos import Polygon, MultiPolygon, Point
from apps.organizations.models import Organization
from apps.geospatial.models import Region, RegionAccess, SatelliteImage, VegetationIndex
from django.utils import timezone
from apps.analytics.models import AgriculturalStressEvent, ConflictEvent
from apps.reports_alerts.models import Alert
from apps.users.models import User

org_fields = {f.name for f in Organization._meta.fields}
org, _ = Organization.objects.get_or_create(name="Kivu Food Security Demo", defaults={k: v for k, v in dict(
    organization_type="humanitarian", contact_email="demo@agrisight.test", is_active=True).items() if k in org_fields})
from allauth.account.models import EmailAddress
for email, utype, staff in [("admin@agrisight.test", "admin", True), ("field@agrisight.test", "humanitarian", False)]:
    u, _ = User.objects.get_or_create(username=email.split("@")[0], defaults=dict(
        email=email, user_type=utype, is_staff=staff, is_superuser=staff, first_name="Test", last_name=utype.title()))
    u.set_password("AgriTest#2026"); u.organization = org; u.save()
    EmailAddress.objects.get_or_create(user=u, email=email, defaults=dict(verified=True, primary=True))

def box(x0, y0, x1, y1):
    return MultiPolygon(Polygon(((x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0))), srid=4326)

regions = []
for name, code, prov, b in [
    ("Rutshuru", "CD6105", "North Kivu", (29.2, -1.4, 29.6, -0.9)),
    ("Masisi", "CD6104", "North Kivu", (28.7, -1.6, 29.1, -1.2)),
    ("Kalehe", "CD6206", "Sud-Kivu", (28.6, -2.2, 29.0, -1.8)),
]:
    r, _ = Region.objects.get_or_create(code=code, defaults=dict(name=name, province=prov, country="DRC", geometry=box(*b), area_hectares=150000))
    RegionAccess.objects.get_or_create(organization=org, region=r, defaults=dict(access_level="full") if "access_level" in {f.name for f in RegionAccess._meta.fields} else {})
    regions.append(r)

today = dt.date.today()
for i, r in enumerate(regions):
    ev, _ = AgriculturalStressEvent.objects.get_or_create(region=r, detection_date=today - dt.timedelta(days=3 + i), defaults=dict(
        stress_type="water", severity=3 + i % 3, affected_area_hectares=1200 * (i + 1),
        description=f"NDVI drop detected in {r.name}", geometry=r.geometry))
    c = r.geometry.centroid
    ConflictEvent.objects.get_or_create(region=r, event_date=today - dt.timedelta(days=5 + i), defaults=dict(
        event_type="Violence against civilians", description=f"Reported clashes near {r.name}", source="QA seed",
        intensity=2 + i, location=Point(c.x, c.y, srid=4326), affected_radius_km=10))
    a, created = Alert.objects.get_or_create(organization=org, title=f"Crop stress in {r.name}", defaults=dict(
        alert_type="stress", severity="critical", message="Seeded alert for QA", related_stress_event=ev))
    if created:
        a.regions.add(r)
# A few processed Sentinel-2 scenes with NDVI/EVI so the dashboard trend and
# region rows have real values (one region is left without imagery on purpose).
for r_idx, r in enumerate(regions[:2]):
    for d_idx, days_ago in enumerate((25, 15, 5)):
        acquired = timezone.now() - dt.timedelta(days=days_ago)
        img, created = SatelliteImage.objects.get_or_create(
            region=r, acquisition_date__date=acquired.date(), defaults=dict(
                acquisition_date=acquired, satellite_name="Sentinel-2", cloud_cover_percentage=8.0,
                resolution_meters=10, bands_available=["B04", "B08"], image_path="qa/seed.tif", is_processed=True))
        if created:
            ndvi = 0.68 - 0.06 * d_idx - 0.05 * r_idx
            VegetationIndex.objects.create(satellite_image=img, index_type="NDVI", mean_value=ndvi,
                                           min_value=ndvi - 0.2, max_value=ndvi + 0.15, std_deviation=0.08, raster_path="qa/ndvi.tif")
            VegetationIndex.objects.create(satellite_image=img, index_type="EVI", mean_value=ndvi * 0.7,
                                           min_value=0.1, max_value=0.7, std_deviation=0.06, raster_path="qa/evi.tif")

print("seeded", Region.objects.count(), "regions,", VegetationIndex.objects.count(), "vegetation indices,", AgriculturalStressEvent.objects.count(), "stress events,", Alert.objects.count(), "alerts")
