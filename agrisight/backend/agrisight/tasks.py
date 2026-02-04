from sentinelhub import SHConfig, BBox, CRS, DataCollection
from sentinelhub import SentinelHubRequest, MimeType
from datetime import datetime, timedelta
import os

class SentinelIngestion:
    def __init__(self):
        self.config = SHConfig()
        self.config.sh_client_id = os.getenv('SENTINEL_HUB_CLIENT_ID')
        self.config.sh_client_secret = os.getenv('SENTINEL_HUB_CLIENT_SECRET')
        
    def fetch_imagery(self, bbox, date_range):
        """
        Fetch Sentinel-2 imagery for specified AOI and date range
        
        Args:
            bbox: BBox object with coordinates
            date_range: Tuple of (start_date, end_date)
        
        Returns:
            List of TIFF images
        """
        evalscript = """
        //VERSION=3
        function setup() {
            return {
                input: [{
                    bands: ["B02", "B03", "B04", "B08"],
                    units: "DN"
                }],
                output: {
                    bands: 4,
                    sampleType: "INT16"
                }
            };
        }
        
        function evaluatePixel(sample) {
            return [sample.B08, sample.B04, sample.B03, sample.B02];
        }
        """
        
        request = SentinelHubRequest(
            evalscript=evalscript,
            input_data=[
                SentinelHubRequest.input_data(
                    data_collection=DataCollection.SENTINEL2_L2A,
                    time_interval=date_range,
                    maxcc=0.3  # Max cloud coverage
                )
            ],
            responses=[
                SentinelHubRequest.output_response('default', MimeType.TIFF)
            ],
            bbox=bbox,
            size=[512, 512],
            config=self.config
        )
        
        return request.get_data()

#Google Earth Engine integration
import ee

# Initialize (requires authentication)
ee.Initialize()

def get_landsat_ndvi(aoi, start_date, end_date):
    """
    Calculate NDVI from Landsat 8 imagery
    """
    # Define AOI
    geometry = ee.Geometry.Rectangle(aoi)
    
    # Filter collection
    collection = (ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
        .filterBounds(geometry)
        .filterDate(start_date, end_date)
        .filter(ee.Filter.lt('CLOUD_COVER', 30)))
    
    # Calculate NDVI
    def calculate_ndvi(image):
        ndvi = image.normalizedDifference(['SR_B5', 'SR_B4']).rename('NDVI')
        return image.addBands(ndvi)
    
    ndvi_collection = collection.map(calculate_ndvi)
    
    # Export to Drive (manual download required)
    task = ee.batch.Export.image.toDrive(
        image=ndvi_collection.median().select('NDVI'),
        description='kivu_ndvi',
        scale=30,
        region=geometry
    )
    task.start()
    
    return task