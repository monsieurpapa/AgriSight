"""
Management command to load OCHA COD-AB admin2 boundaries for DRC target provinces.

Idempotent: uses update_or_create on (name, province, country).
Run in Docker entrypoint after migrate.

Usage:
    python manage.py load_ocha_boundaries
    python manage.py load_ocha_boundaries --geojson /path/to/drc_admin2.geojson
    python manage.py load_ocha_boundaries --url https://...
"""

import logging
import tempfile
import os
import requests
import geopandas as gpd
from django.contrib.gis.geos import GEOSGeometry, MultiPolygon, Polygon
from django.core.management.base import BaseCommand

logger = logging.getLogger(__name__)

OCHA_HDX_URL = (
    "https://data.humdata.org/dataset/cod-ab-cod/"
    "resource/drc_admbnda_adm2_ocha_itos_20190401.geojson"
)

TARGET_PROVINCES = {"north kivu", "sud-kivu", "south kivu", "ituri"}

ACLED_ALIASES = {
    "Beni": ["Beni Territory", "Beni-Ville"],
    "Butembo": ["Butembo Territory"],
    "Goma": ["Goma Territory", "Nyiragongo"],
    "Masisi": ["Masisi Territory"],
    "Rutshuru": ["Rutshuru Territory"],
    "Walikale": ["Walikale Territory"],
    "Bukavu": ["Bukavu Territory"],
    "Uvira": ["Uvira Territory"],
    "Fizi": ["Fizi Territory"],
    "Kalehe": ["Kalehe Territory"],
    "Djugu": ["Djugu Territory"],
    "Irumu": ["Irumu Territory"],
    "Bunia": ["Bunia Territory"],
}

PROVINCE_NORMALISATION = {
    "south kivu": "Sud-Kivu",
    "sud-kivu": "Sud-Kivu",
    "nord-kivu": "North Kivu",
    "north kivu": "North Kivu",
    "ituri": "Ituri",
}


class Command(BaseCommand):
    help = "Load OCHA COD-AB admin2 boundaries for DRC target provinces (idempotent)"

    def add_arguments(self, parser):
        parser.add_argument("--geojson", type=str, help="Path to local GeoJSON file")
        parser.add_argument("--url", type=str, default=OCHA_HDX_URL, help="URL to download GeoJSON from")
        parser.add_argument("--dry-run", action="store_true", help="Parse but do not write to DB")

    def handle(self, *args, **options):
        from apps.geospatial.models import Region

        geojson_path = options.get("geojson")
        url = options.get("url")
        dry_run = options.get("dry_run", False)

        gdf = self._load_geodataframe(geojson_path, url)
        if gdf is None or gdf.empty:
            self.stderr.write("No features loaded — aborting.")
            return

        # Ensure WGS84
        if gdf.crs is not None and not gdf.crs.equals("EPSG:4326"):
            gdf = gdf.to_crs("EPSG:4326")

        created = 0
        updated = 0

        for _, row in gdf.iterrows():
            name = self._extract_name(row)
            province_raw = self._extract_province(row)

            if not name or not province_raw:
                continue

            province_lower = province_raw.lower()
            if province_lower not in TARGET_PROVINCES:
                continue

            province = PROVINCE_NORMALISATION.get(province_lower, province_raw.title())
            aliases = ACLED_ALIASES.get(name, [])
            geometry = self._shapely_to_geos(row.geometry)
            if geometry is None:
                self.stderr.write(f"Skipping {name} — invalid geometry")
                continue

            if dry_run:
                self.stdout.write(f"[DRY RUN] Would upsert: {name} / {province}")
                continue

            pcode = row.get("ADM2_PCODE") or row.get("adm2_pcode") or ""
            _, was_created = Region.objects.update_or_create(
                name=name,
                province=province,
                country="Democratic Republic of Congo",
                defaults={
                    "geometry": geometry,
                    "acled_name_aliases": aliases,
                    "code": pcode,
                },
            )
            if was_created:
                created += 1
                self.stdout.write(f"  Created: {name} ({province})")
            else:
                updated += 1

        if not dry_run:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Done. Created: {created}, updated: {updated} district boundaries."
                )
            )

    def _load_geodataframe(self, path, url):
        if path:
            try:
                return gpd.read_file(path, engine="fiona")
            except Exception as exc:
                self.stderr.write(f"Failed to load local file: {exc}")
                return None

        self.stdout.write(f"Downloading boundaries from {url} ...")
        tmp_path = None
        try:
            resp = requests.get(url, timeout=60)
            resp.raise_for_status()
            with tempfile.NamedTemporaryFile(suffix=".geojson", delete=False) as tmp:
                tmp_path = tmp.name
                tmp.write(resp.content)
            return gpd.read_file(tmp_path, engine="fiona")
        except Exception as exc:
            self.stderr.write(f"Failed to download/parse boundaries: {exc}")
            return None
        finally:
            if tmp_path:
                try:
                    os.unlink(tmp_path)
                except OSError:
                    pass

    def _extract_name(self, row) -> str:
        for key in ("ADM2_EN", "adm2_en", "NAME_2", "name", "ADM2NAME"):
            val = row.get(key)
            if val:
                return str(val).strip()
        return ""

    def _extract_province(self, row) -> str:
        for key in ("ADM1_EN", "adm1_en", "NAME_1", "province", "ADM1NAME"):
            val = row.get(key)
            if val:
                return str(val).strip()
        return ""

    def _shapely_to_geos(self, geom) -> MultiPolygon | None:
        if geom is None or geom.is_empty:
            return None
        try:
            geos = GEOSGeometry(geom.wkt, srid=4326)
            if isinstance(geos, Polygon):
                return MultiPolygon(geos)
            if isinstance(geos, MultiPolygon):
                return geos
            return None
        except Exception as exc:
            logger.warning("Geometry conversion error: %s", exc)
            return None
