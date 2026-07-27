import os
import re
import requests
import json
import logging
from dateutil import parser as date_parser
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
from django.conf import settings

logger = logging.getLogger(__name__)

# Matches the path produced by create_batch_request's defaultTilePath template:
# s3://{bucket}/ndvi/{tileid}/{date}.tif
# The exact string Sentinel Hub substitutes for {date} isn't pinned down in the
# public Batch V2 docs, so this only splits tile_id from the date stem -- the
# stem itself is parsed leniently with dateutil in list_ndvi_outputs().
NDVI_OUTPUT_KEY_RE = re.compile(r"^ndvi/(?P<tile_id>[^/]+)/(?P<date_stem>[^/]+)\.tif$")

class BatchClient:
    """
    Client for Sentinel Hub Batch V2 API via Copernicus Dataspace Ecosystem.
    """
    
    TOKEN_URL = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"
    BATCH_URL = "https://sh.dataspace.copernicus.eu/api/v2/batch/process"
    
    def __init__(self):
        self.client_id = os.environ.get('SENTINEL_HUB_CLIENT_ID')
        self.client_secret = os.environ.get('SENTINEL_HUB_CLIENT_SECRET')
        self.s3_bucket = os.environ.get('S3_BUCKET_NAME')
        self.s3_access_key = os.environ.get('S3_ACCESS_KEY')
        self.s3_secret_key = os.environ.get('S3_SECRET_KEY')
        self.s3_endpoint_url = os.environ.get('S3_REGION_URL', 'https://s3.waw2-1.cloudferro.com')
        
        if not all([self.client_id, self.client_secret, self.s3_bucket, self.s3_access_key, self.s3_secret_key]):
            logger.warning("BatchClient initialized with missing credentials. Batch processing will fail.")

    def get_token(self):
        """
        Obtain OAuth2 token using Client Credentials flow.
        """
        try:
            client = BackendApplicationClient(client_id=self.client_id)
            oauth = OAuth2Session(client=client)
            token = oauth.fetch_token(
                token_url=self.TOKEN_URL, 
                client_id=self.client_id, 
                client_secret=self.client_secret
            )
            return token['access_token']
        except Exception as e:
            logger.error(f"Failed to obtain Sentinel Hub token: {e}")
            raise

    def create_batch_request(self, bbox, time_range, description="Batch Request"):
        """
        Create a new batch processing request.
        
        Args:
            bbox (list): [min_lon, min_lat, max_lon, max_lat]
            time_range (tuple): (start_date_iso, end_date_iso)
            description (str): Description of the request
            
        Returns:
            dict: API response containing request ID
        """
        token = self.get_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # S3 Output Path Pattern
        # Result will be: s3://bucket/ndvi/<req_id>/<tile_id>/<date>.tif
        output_prefix = f"ndvi" 
        
        payload = {
            "processRequest": {
                "input": {
                    "bounds": {
                        "bbox": bbox
                    },
                    "data": [{
                        "type": "sentinel-2-l2a",
                        "dataFilter": {
                            "timeRange": {
                                "from": time_range[0],
                                "to": time_range[1]
                            }
                        }
                    }]
                },
                "output": {
                    "responses": [{
                        "identifier": "default",
                        "format": { "type": "image/tiff" }
                    }]
                },
                "evalscript": self._get_ndvi_evalscript()
            },
            "tilingGrid": {
                "id": 1,
                "resolution": 10.0
            },
            "output": {
                "defaultTilePath": f"s3://{self.s3_bucket}/{output_prefix}/{{tileid}}/{{date}}.tif",
                "delivery": {
                    "type": "S3",
                    "params": {
                        "url": self.s3_endpoint_url,
                        "accessKey": self.s3_access_key,
                        "secretAccessKey": self.s3_secret_key,
                        "bucketName": self.s3_bucket
                    }
                }
            },
            "description": description
        }
        
        response = requests.post(self.BATCH_URL, headers=headers, json=payload)
        
        if response.status_code in [200, 201]:
            return response.json()
        else:
            logger.error(f"Batch creation failed: {response.text}")
            raise Exception(f"Batch creation failed: {response.text}")

    def start_batch_request(self, request_id):
        """
        Start a created batch request.
        """
        token = self.get_token()
        url = f"{self.BATCH_URL}/{request_id}/analyse" # Analyse first
        headers = {"Authorization": f"Bearer {token}"}
        
        # Trigger Analysis
        logger.info(f"Analyzing batch request {request_id}...")
        resp = requests.post(url, headers=headers)
        if resp.status_code not in [200, 204]:
             raise Exception(f"Analysis trigger failed: {resp.text}")
             
        # Note: In a real async flow, we would wait for ANALYSIS_DONE separately.
        # For simplicity here, we might just assume logic handles the transition or we assume
        # the user calls 'start' after analysis.
        # But Sentinel Hub requires 'analyse' -> wait -> 'start'.
        
        # Let's just create the start method, the caller (task) handles the flow.
        return True

    def execute_start(self, request_id):
        """
        Actually calls start after analysis.
        """
        token = self.get_token()
        url = f"{self.BATCH_URL}/{request_id}/start"
        headers = {"Authorization": f"Bearer {token}"}
        resp = requests.post(url, headers=headers)
        if resp.status_code not in [200, 204]:
             raise Exception(f"Start failed: {resp.text}")
        return True

    def get_request_status(self, request_id):
        """
        Get status of a batch request.
        """
        token = self.get_token()
        url = f"{self.BATCH_URL}/{request_id}"
        headers = {"Authorization": f"Bearer {token}"}

        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json().get('status')
        return None

    def get_s3_client(self):
        """
        Boto3 S3 client configured for the CloudFerro-compatible output bucket.
        Batch V2 has no API for listing per-request output tiles -- results are
        only discoverable by listing the S3 bucket/prefix we control via the
        request's `output.delivery` config (see create_batch_request).
        """
        import boto3
        return boto3.client(
            's3',
            endpoint_url=self.s3_endpoint_url,
            aws_access_key_id=self.s3_access_key,
            aws_secret_access_key=self.s3_secret_key,
        )

    def list_ndvi_outputs(self, prefix="ndvi/"):
        """
        List NDVI output tiles written to S3, parsed from the key.

        NOTE: defaultTilePath in create_batch_request is `ndvi/{tileid}/{date}.tif`
        with no request_id segment, so outputs from different batch requests that
        happen to share a tile+date are not distinguishable by key alone. Callers
        must additionally filter by their own request's time range to scope results
        to "probably mine" -- this is a known limitation, not a guarantee of
        per-request isolation. See TODOS.md.

        Returns:
            list[dict]: [{'key': str, 'tile_id': str, 'date': datetime|None}, ...]
        """
        s3 = self.get_s3_client()
        paginator = s3.get_paginator('list_objects_v2')
        results = []
        for page in paginator.paginate(Bucket=self.s3_bucket, Prefix=prefix):
            for obj in page.get('Contents', []):
                key = obj['Key']
                match = NDVI_OUTPUT_KEY_RE.match(key)
                if not match:
                    logger.warning(f"Skipping S3 key with unexpected NDVI output format: {key}")
                    continue
                try:
                    parsed_date = date_parser.parse(match.group('date_stem'))
                except (ValueError, OverflowError):
                    logger.warning(f"Could not parse date from S3 key: {key}")
                    continue
                results.append({
                    'key': key,
                    'tile_id': match.group('tile_id'),
                    'date': parsed_date,
                })
        return results

    def download_output(self, key, local_path):
        """
        Download a single output object from S3 to a local path.
        """
        s3 = self.get_s3_client()
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        s3.download_file(self.s3_bucket, key, local_path)
        return local_path

    def _get_ndvi_evalscript(self):
        return """
        //VERSION=3
        function setup() {
            return {
                input: ["B04", "B08"],
                output: { bands: 1, sampleType: "FLOAT32" }
            };
        }
        function evaluatePixel(sample) {
            let ndvi = (sample.B08 - sample.B04) / (sample.B08 + sample.B04);
            return [ndvi];
        }
        """
