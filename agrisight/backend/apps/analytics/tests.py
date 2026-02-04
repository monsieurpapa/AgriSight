from datetime import date
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.test import Client
from django.contrib.gis.geos import MultiPolygon, Polygon, Point

from apps.organizations.models import Organization
from apps.geospatial.models import Region, RegionAccess
from .models import AgriculturalStressEvent, ConflictEvent


User = get_user_model()


class AnalyticsSummaryTests(TestCase):
    def setUp(self):
        self.client = Client()

        self.org_a = Organization.objects.create(
            name="Org A",
            organization_type="humanitarian",
            contact_email="a@example.com"
        )
        self.org_b = Organization.objects.create(
            name="Org B",
            organization_type="cooperative",
            contact_email="b@example.com"
        )

        geom = MultiPolygon(Polygon((
            (28.5, -1.5),
            (30.0, -1.5),
            (30.0, 0.5),
            (28.5, 0.5),
            (28.5, -1.5),
        )))

        self.region_a = Region.objects.create(
            name="Region A",
            country="DRC",
            province="North Kivu",
            geometry=geom
        )
        self.region_b = Region.objects.create(
            name="Region B",
            country="DRC",
            province="South Kivu",
            geometry=geom
        )

        RegionAccess.objects.create(
            organization=self.org_a,
            region=self.region_a,
            access_level="view",
            start_date=date.today()
        )
        RegionAccess.objects.create(
            organization=self.org_b,
            region=self.region_b,
            access_level="view",
            start_date=date.today()
        )

        self.user_a = User.objects.create_user(
            username="usera",
            email="usera@example.com",
            password="StrongPass123",
            user_type="humanitarian",
            organization=self.org_a
        )
        self.user_b = User.objects.create_user(
            username="userb",
            email="userb@example.com",
            password="StrongPass123",
            user_type="cooperative",
            organization=self.org_b
        )

        AgriculturalStressEvent.objects.create(
            region=self.region_a,
            detection_date=date.today(),
            stress_type="water",
            severity=3,
            affected_area_hectares=10.0,
            description="Stress in A",
            geometry=geom
        )
        AgriculturalStressEvent.objects.create(
            region=self.region_b,
            detection_date=date.today(),
            stress_type="disease",
            severity=2,
            affected_area_hectares=5.0,
            description="Stress in B",
            geometry=geom
        )

        ConflictEvent.objects.create(
            region=self.region_a,
            event_date=date.today(),
            event_type="Clash",
            description="Conflict A",
            source="Local",
            intensity=2,
            location=Point(29.0, -1.0),
            affected_radius_km=5.0
        )
        ConflictEvent.objects.create(
            region=self.region_b,
            event_date=date.today(),
            event_type="Clash",
            description="Conflict B",
            source="Local",
            intensity=3,
            location=Point(29.0, -1.0),
            affected_radius_km=5.0
        )

    def test_stress_event_summary_scoped_to_org(self):
        self.client.force_login(self.user_a)
        response = self.client.get("/api/v1/analytics/stress-events/summary/?days=30")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["total_events"], 1)
        self.assertIn("events_by_type", data)
        self.assertEqual(sum(data["events_by_type"].values()), 1)

    def test_conflict_event_summary_scoped_to_org(self):
        self.client.force_login(self.user_a)
        response = self.client.get("/api/v1/analytics/conflict-events/summary/?days=30")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["total_events"], 1)
        self.assertIn("events_by_type", data)
        self.assertEqual(sum(data["events_by_type"].values()), 1)

    def test_stress_event_list_scoped_to_org(self):
        self.client.force_login(self.user_a)
        response = self.client.get("/api/v1/analytics/stress-events/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        results = data.get("results") or data.get("features") or data
        if isinstance(results, dict) and "features" in results:
            results = results["features"]
        self.assertEqual(len(results), 1)
        event = results[0]
        if isinstance(event, dict) and "properties" in event:
            region_id = event["properties"].get("region")
        else:
            region_id = event.get("region")
        self.assertEqual(str(region_id), str(self.region_a.id))

    def test_conflict_event_list_scoped_to_org(self):
        self.client.force_login(self.user_a)
        response = self.client.get("/api/v1/analytics/conflict-events/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        results = data.get("results") or data.get("features") or data
        if isinstance(results, dict) and "features" in results:
            results = results["features"]
        self.assertEqual(len(results), 1)
        event = results[0]
        if isinstance(event, dict) and "properties" in event:
            region_id = event["properties"].get("region")
        else:
            region_id = event.get("region")
        self.assertEqual(str(region_id), str(self.region_a.id))
