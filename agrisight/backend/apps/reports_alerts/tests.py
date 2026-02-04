from datetime import date
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.test import Client
from django.contrib.gis.geos import MultiPolygon, Polygon

from apps.organizations.models import Organization
from apps.geospatial.models import Region
from .models import Report


User = get_user_model()


class ReportsAccessTests(TestCase):
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

        self.report_a = Report.objects.create(
            title="Report A",
            organization=self.org_a,
            report_type="stress",
            time_period_start=date.today(),
            time_period_end=date.today(),
            content={"summary": "A"},
            file_path="reports/report_a.json"
        )
        self.report_a.regions.add(self.region_a)

        self.report_b = Report.objects.create(
            title="Report B",
            organization=self.org_b,
            report_type="water",
            time_period_start=date.today(),
            time_period_end=date.today(),
            content={"summary": "B"},
            file_path="reports/report_b.json"
        )
        self.report_b.regions.add(self.region_b)

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

    def test_report_list_scoped_to_org(self):
        self.client.force_login(self.user_a)
        response = self.client.get("/api/v1/reports-alerts/reports/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        results = data.get("results") or data
        self.assertEqual(len(results), 1)
        self.assertEqual(str(results[0]["id"]), str(self.report_a.id))

    def test_report_detail_scoped_to_org(self):
        self.client.force_login(self.user_a)
        response = self.client.get(f"/api/v1/reports-alerts/reports/{self.report_b.id}/")
        self.assertEqual(response.status_code, 404)

    def test_alert_list_scoped_to_org(self):
        from .models import Alert

        alert_a = Alert.objects.create(
            organization=self.org_a,
            alert_type="stress",
            severity="warning",
            title="Alert A",
            message="Message A"
        )
        alert_a.regions.add(self.region_a)

        alert_b = Alert.objects.create(
            organization=self.org_b,
            alert_type="system",
            severity="info",
            title="Alert B",
            message="Message B"
        )
        alert_b.regions.add(self.region_b)

        self.client.force_login(self.user_a)
        response = self.client.get("/api/v1/reports-alerts/alerts/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        results = data.get("results") or data
        self.assertEqual(len(results), 1)
        self.assertEqual(str(results[0]["id"]), str(alert_a.id))

    def test_mark_alert_as_read_scoped_to_org(self):
        from .models import Alert

        alert = Alert.objects.create(
            organization=self.org_a,
            alert_type="stress",
            severity="warning",
            title="Alert A",
            message="Message A"
        )
        alert.regions.add(self.region_a)

        self.client.force_login(self.user_a)
        response = self.client.post(f"/api/v1/reports-alerts/alerts/{alert.id}/mark-read/")
        self.assertEqual(response.status_code, 200)
        alert.refresh_from_db()
        self.assertTrue(alert.is_read)
