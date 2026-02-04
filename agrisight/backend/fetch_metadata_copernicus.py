import requests
import json
from datetime import datetime, timedelta

def main():
    print("--- Fetching Copernicus Dataspace Sentinel-2 Metadata ---")
    
    # 1. Configuration
    # Endpoint
    url = "https://catalogue.dataspace.copernicus.eu/odata/v1/Products"
    
    # 2. Define AOI (North Kivu approx)
    # BBox: [29.0, -1.8, 29.5, -1.3] (min_lon, min_lat, max_lon, max_lat)
    # Polygon WKT for OData: POLYGON((lon1 lat1, lon2 lat1, lon2 lat2, lon1 lat2, lon1 lat1))
    p1 = "29.0 -1.8"
    p2 = "29.5 -1.8"
    p3 = "29.5 -1.3"
    p4 = "29.0 -1.3"
    # Note: OData geography literals might vary, usually geography'SRID=4326;POLYGON((...))'
    polygon = f"POLYGON(({p1}, {p2}, {p3}, {p4}, {p1}))"
    
    # 3. Time range (Last 30 days)
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=30)
    start_date_str = start_date.strftime('%Y-%m-%dT%H:%M:%S.000Z')
    
    print(f"AOI Polygon: {polygon}")
    print(f"Start Date: {start_date_str}")
    
    # 4. Construct OData Query
    # Collection: SENTINEL-2
    # Filter by Collection, Geometry, and Date
    filter_query = (
        f"Collection/Name eq 'SENTINEL-2' and "
        f"OData.CSC.Intersects(area=geography'SRID=4326;{polygon}') and "
        f"ContentDate/Start gt {start_date_str}"
    )
    
    # Select fields to keep response light
    # We want Name, Id, ContentDate, and Attributes (for Cloud Cover)
    # Attributes are usually a list, handled separately or fetching minimal fields
    params = {
        "$filter": filter_query,
        "$orderby": "ContentDate/Start desc",
        "$top": 20, # Limit to top 20 for readability
        # "$select": "Id,Name,ContentDate,Attributes" # API might be strict on casing or selection
    }
    
    print("\nSending Request to Copernicus Dataspace...")
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        products = data.get('value', [])
        
        print(f"\nFound {len(products)} scenes (showing max 20):")
        
        for product in products:
            prod_id = product.get('Id')
            name = product.get('Name')
            start_time = product.get('ContentDate', {}).get('Start')
            
            # Extract Cloud Cover if available in Attributes
            cloud_cover = "N/A"
            attributes = product.get('Attributes', [])
            for attr in attributes:
                if attr.get('Name') == 'cloudCover':
                    cloud_cover = attr.get('Value')
                    break
            
            print(f"- Date: {start_time} | Cloud Cover: {cloud_cover}% | ID: {prod_id}")
            # print(f"  Name: {name}")
            
    except Exception as e:
        print(f"Error fetching metadata: {e}")
        if 'response' in locals():
            print(f"Response Body: {response.text[:500]}")

if __name__ == "__main__":
    main()
