# Research Notes: Sentinel Hub Batch V2 Integration

**Source**: [Copernicus Dataspace Documentation](https://documentation.dataspace.copernicus.eu/APIs/SentinelHub/BatchV2/Examples.html)

## Workflow
The Batch V2 API follows a 3-step process for large-scale data processing:

1.  **Create Request**: Define the processing graph (evalscript), input data (Sentinel-2, etc.), tiling grid, and output configuration (usually S3 bucket).
2.  **Analyse**: (Optional/Implicit?) Validate the request and estimate tile count/cost.
3.  **Start**: Trigger the processing.
4.  **Monitor**: Poll status (CREATED -> ANALYSIS_DONE -> PARTIAL -> DONE).

## Key Requirements

### 1. Authentication
- Uses `Authorization: Bearer <access_token>`
- Token obtained via OIDC from `https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token`? (Need to verify endpoint).
- Client Credentials flow (Client ID + Secret).

### 2. Request Structure
POST `.../api/v1/batch/process`

```json
{
  "processRequest": {
    "input": {
      "bounds": {
        "bbox": [...],
        "geometry": ...
      },
      "data": [
        {
          "type": "sentinel-2-l2a",
          "dataFilter": {
            "timeRange": {
              "from": "2023-01-01T00:00:00Z",
              "to": "2023-01-31T23:59:59Z"
            }
          }
        }
      ]
    },
    "output": {
      "responses": [
        {
          "identifier": "default",
          "format": { "type": "image/tiff" }
        }
      ]
    },
    "evalscript": "..."
  },
  "tilingGrid": {
    "id": 1,
    "resolution": 10.0
  },
  "output": {
    "defaultTilePath": "s3://<my-bucket>/<path>/{tileid}/{date}.tif",
    "delivery": {
        "type": "S3",
        "params": {
            "url": "https://s3.waw2-1.cloudferro.com",
            "accessKey": "...",
            "secretAccessKey": "...",
            "bucketName": "..."
        }
    }
  },
  "description": "My batch processing"
}
```

## Integration Challenges
1.  **Storage**: Batch API prefers delivering to Object Storage (S3-compatible). Copernicus Dataspace provides S3 storage? Or do we need our own?
    - *Note*: `s3.waw2-1.cloudferro.com` is the endpoint often used.
2.  **Async Nature**: The backend needs to handle the async workflow (Create -> Start -> Poll -> Download?).
3.  **Authentication**: Need valid OIDC credentials. The previous ones failed.

## Next Steps
1.  Verify if we can use a "Direct Download" or if S3 is mandatory. (Docs usually imply S3 for Batch).
2.  If S3 is mandatory, we might need a bucket.
3.  Alternatively, stick to `Process API` (sync) for smaller regions (which is what we have now), but maybe implement `Process API` correctly with the new OData discovery we just built?
    - Wait, OData finds the *product*. To get the *pixels*, we need `Process API` or `Download API`.
    - Batch is for *large scale*. If user wants "Batch", they likely imply large scale.

