import os
import requests
import json
import time
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session

# Configuration
CLIENT_ID = os.environ.get('SENTINEL_HUB_CLIENT_ID')
CLIENT_SECRET = os.environ.get('SENTINEL_HUB_CLIENT_SECRET')

# Copernicus Dataspace / Sentinel Hub Endpoints
TOKEN_URL = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"
BATCH_URL = "https://sh.dataspace.copernicus.eu/api/v2/batch/process"

# S3 Configuration (Placeholder - User must provide)
S3_BUCKET_NAME = "my-agrisight-bucket"
S3_REGION_URL = "https://s3.waw2-1.cloudferro.com"
S3_ACCESS_KEY = os.environ.get('S3_ACCESS_KEY')
S3_SECRET_KEY = os.environ.get('S3_SECRET_KEY')

def get_token():
    client = BackendApplicationClient(client_id=CLIENT_ID)
    oauth = OAuth2Session(client=client)
    token = oauth.fetch_token(token_url=TOKEN_URL, client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
    return token['access_token']

def create_batch_request(token):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Example payload for NDVI
    payload = {
        "processRequest": {
            "input": {
                "bounds": {
                    "bbox": [29.0, -1.8, 29.5, -1.3]  # North Kivu approx
                },
                "data": [{
                    "type": "sentinel-2-l2a",
                    "dataFilter": {
                        "timeRange": {
                            "from": "2024-01-01T00:00:00Z",
                            "to": "2024-01-31T23:59:59Z"
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
            "evalscript": """
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
        },
        "tilingGrid": {
            "id": 1,
            "resolution": 20.0 # 20m resolution
        },
        "output": {
            "defaultTilePath": f"s3://{S3_BUCKET_NAME}/ndvi/{{tileid}}/{{date}}.tif",
            "delivery": {
                "type": "S3",
                "params": {
                    "url": S3_REGION_URL,
                    "accessKey": S3_ACCESS_KEY,
                    "secretAccessKey": S3_SECRET_KEY,
                    "bucketName": S3_BUCKET_NAME
                }
            }
        },
        "description": "North Kivu NDVI Batch Analysis"
    }

    response = requests.post(BATCH_URL, headers=headers, json=payload)
    if response.status_code in [200, 201]:
        return response.json()
    else:
        print(f"Error creating batch request: {response.text}")
        return None

def start_batch_request(token, request_id):
    url = f"{BATCH_URL}/{request_id}/start"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(url, headers=headers)
    return response.status_code == 204

def analyze_batch_request(token, request_id):
    url = f"{BATCH_URL}/{request_id}/analyse"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(url, headers=headers)
    return response.status_code == 204

def get_request_status(token, request_id):
    url = f"{BATCH_URL}/{request_id}"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    return response.json().get('status')

def main():
    print("--- Sentinel Hub Batch V2 Prototype ---")
    
    if not CLIENT_ID or not CLIENT_SECRET or not S3_ACCESS_KEY:
        print("Missing credentials (CLIENT_ID, CLIENT_SECRET, or S3_ACCESS_KEY).")
        return

    try:
        print("Authenticating...")
        token = get_token()
        print("Authenticated.")
        
        print("Creating Batch Request...")
        request_data = create_batch_request(token)
        if not request_data:
            return
            
        request_id = request_data['id']
        print(f"Request Created: {request_id}")
        
        print("Analyzing Request...")
        analyze_batch_request(token, request_id)
        
        # Poll for ANALYSIS_DONE
        while True:
            status = get_request_status(token, request_id)
            print(f"Status: {status}")
            if status == "ANALYSIS_DONE":
                break
            if status == "FAILED":
                print("Analysis Failed.")
                return
            time.sleep(2)
            
        print("Starting Processing...")
        start_batch_request(token, request_id)
        print("Processing Started. Check S3 bucket for results.")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
