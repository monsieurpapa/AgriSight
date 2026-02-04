from datetime import date
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.test import Client
from django.contrib.gis.geos import MultiPolygon, Polygon

from apps.organizations.models import Organization
from .models import Region, RegionAccess, SatelliteImage, VegetationIndex
from django.utils import timezone


User = get_user_model()


class RegionAccessTests(TestCase):
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

        self.admin = User.objects.create_user(
            username="admin",
            email="admin@example.com",
            password="StrongPass123",
            user_type="admin"
        )

    def test_region_list_scoped_to_organization(self):
        self.client.force_login(self.user_a)
        response = self.client.get("/api/v1/geospatial/regions/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["count"], 1)
        results = data.get("results") or data
        if isinstance(results, dict) and "features" in results:
            results = results["features"]
            region_name = results[0]["properties"]["name"]
        else:
            region_name = results[0]["name"]
        self.assertEqual(region_name, "Region A")

    def test_region_list_admin_sees_all(self):
        self.client.force_login(self.admin)
        response = self.client.get("/api/v1/geospatial/regions/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["count"], 2)

    def test_region_create_requires_manage_regions(self):
        self.client.force_login(self.user_a)
        response = self.client.post("/api/v1/geospatial/regions/", {
            "name": "Region C",
            "country": "DRC",
            "province": "Ituri",
            "geometry": self.region_a.geometry.wkt
        })
        self.assertEqual(response.status_code, 403)

    def test_data_quality_summary_scoped_to_org(self):
        SatelliteImage.objects.create(
            region=self.region_a,
            acquisition_date=timezone.now(),
            satellite_name='Sentinel-2',
            cloud_cover_percentage=10.0,
            resolution_meters=10.0,
            bands_available=['B02', 'B03', 'B04', 'B08'],
            image_path='/test/path_a.tif',
            is_processed=True
        )
        SatelliteImage.objects.create(
            region=self.region_b,
            acquisition_date=timezone.now(),
            satellite_name='Sentinel-2',
            cloud_cover_percentage=20.0,
            resolution_meters=10.0,
            bands_available=['B02', 'B03', 'B04', 'B08'],
            image_path='/test/path_b.tif',
            is_processed=False
        )
        image_a = SatelliteImage.objects.filter(region=self.region_a).first()
        VegetationIndex.objects.create(
            satellite_image=image_a,
            index_type='NDVI',
            mean_value=0.6,
            min_value=0.2,
            max_value=0.9,
            std_deviation=0.1,
            raster_path='/test/ndvi_a.tif'
        )

        self.client.force_login(self.user_a)
        response = self.client.get("/api/v1/geospatial/data-quality/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['regions']['total'], 1)
        self.assertEqual(data['satellite_images']['total'], 1)
        self.assertEqual(data['vegetation_indices']['total'], 1)
