# Satellite Data Sources and APIs for AgriSight Project

## Free Satellite Imagery Providers

### 1. EOSDA LandViewer
- **Available Imagery**: Landsat 7 and 8, Sentinel 1 and 2, CBERS-4, MODIS, NAIP aerial data
- **Historical Data**: Landsat 4 and 5
- **Commercial Preview**: Kompsat-2/3/3A, SuperView-1/2/3/4, Gaofen-1/2, Ziyuan-3, GEOSAT-2, TripleSat
- **Resolution**: Up to 40 cm per pixel (commercial)
- **Analysis Tools**: 
  - Band combinations and indices (NDVI, NBR, SAVI)
  - Custom index builder
  - Time series analysis
  - Clustering
  - Change detection
- **Advantages**: User-friendly interface, built-in analysis tools, free download options
- **Relevance for AgriSight**: Excellent platform for initial analysis and visualization of agricultural areas in DRC

### 2. USGS EarthExplorer
- **Available Imagery**: Landsat missions, MODIS, ASTER, VIIRS
- **Additional Data**: Resourcesat-1/2, IKONOS-2, OrbView-3, historical SPOT data
- **Features**: 40+ years of historical data, feature-based search
- **Advantages**: Extensive historical archive, variety of data types
- **Relevance for AgriSight**: Valuable for long-term land use change analysis in DRC agricultural regions

### 3. NASA Earthdata Search
- **Available Imagery**: Aqua and Terra, ENVISAT, GOES, NOAA satellites, METEOSAT, Suomi-NPP, Nimbus, CALIPSO, Landsat
- **Focus Areas**: Atmosphere, environment, ocean, land cover, vegetation, ice cover, topography
- **Advantages**: Comprehensive NASA Earth science data
- **Relevance for AgriSight**: Additional data sources for environmental factors affecting agriculture

## Key Satellite Systems for Agricultural Monitoring

### 1. Sentinel-2
- **Spatial Resolution**: 10m
- **Temporal Resolution**: Every 3-5 days (depending on the area)
- **Spectral Bands**: 13 bands in visible, near infrared, and short wave infrared
- **Advantages**: Good balance of spatial and temporal resolution, free access
- **Relevance for AgriSight**: Primary data source for regular crop monitoring in DRC

### 2. Landsat 8
- **Spatial Resolution**: 30m
- **Temporal Resolution**: Every 16 days
- **Spectral Bands**: 11 bands covering visible, near infrared, short wave infrared, and thermal
- **Advantages**: Long-term historical data, thermal band for moisture stress
- **Relevance for AgriSight**: Complementary to Sentinel-2, useful for thermal analysis

### 3. MODIS
- **Spatial Resolution**: 250m to 1km
- **Temporal Resolution**: Daily
- **Advantages**: Excellent for broad-scale monitoring, long time series
- **Relevance for AgriSight**: Regional-scale vegetation monitoring, drought assessment

### 4. Commercial High-Resolution Options
- **Platforms**: Planet Labs, Airbus Spot 6, Pléiades
- **Resolution**: 0.5m to 5m
- **Advantages**: Very high detail for targeted analysis
- **Relevance for AgriSight**: Detailed analysis of specific agricultural stress zones

## APIs and Platforms for Processing

### 1. Google Earth Engine
- **Description**: Cloud-based platform for planetary-scale geospatial analysis
- **Data Catalog**: Multi-petabyte catalog of satellite imagery and geospatial datasets
- **Agriculture-Specific Datasets**:
  - Crop type maps
  - Evapotranspiration data
  - Cocoa probability models
  - Terrace maps
  - Active cropland markers
- **Advantages**: 
  - Powerful cloud computing
  - No need to download raw data
  - JavaScript and Python APIs
  - Pre-processed datasets
- **Relevance for AgriSight**: Primary platform for large-scale processing of satellite data for DRC

### 2. Sentinel Hub
- **Description**: API for accessing and processing Sentinel, Landsat, and other satellite data
- **Features**: On-demand processing, custom band combinations, various indices
- **Advantages**: Simplified access to data, cloud-based processing
- **Relevance for AgriSight**: Alternative API for accessing Sentinel data

### 3. Planet API
- **Description**: Access to Planet's satellite imagery
- **Features**: Daily high-resolution imagery
- **Advantages**: Frequent revisit, high resolution
- **Relevance for AgriSight**: Potential commercial option for high-frequency monitoring

## Vegetation Indices for Agricultural Monitoring

### 1. NDVI (Normalized Difference Vegetation Index)
- **Purpose**: Measure of vegetation health and density
- **Calculation**: (NIR - Red) / (NIR + Red)
- **Relevance for AgriSight**: Primary index for crop health monitoring

### 2. EVI (Enhanced Vegetation Index)
- **Purpose**: Improved vegetation index with reduced atmospheric influences
- **Relevance for AgriSight**: Better performance in areas with atmospheric interference

### 3. NDWI (Normalized Difference Water Index)
- **Purpose**: Measure of vegetation water content
- **Relevance for AgriSight**: Drought and water stress monitoring

### 4. NDMI (Normalized Difference Moisture Index)
- **Purpose**: Measure of vegetation moisture content
- **Relevance for AgriSight**: Agricultural drought assessment

## Implementation Strategy for AgriSight

1. **Primary Data Sources**:
   - Sentinel-2 (10m resolution, 3-5 day revisit)
   - Landsat 8 (30m resolution, 16-day revisit)
   - MODIS (250m-1km resolution, daily)

2. **Processing Platform**:
   - Google Earth Engine for large-scale processing
   - EOSDA LandViewer for visualization and initial analysis

3. **Key Indices for Monitoring**:
   - NDVI for crop health
   - NDWI/NDMI for water stress
   - Custom indices for specific crop types in DRC

4. **Temporal Analysis**:
   - Historical baseline using Landsat archive
   - Current monitoring using Sentinel-2
   - Rapid response using MODIS

5. **Spatial Focus**:
   - Priority monitoring of North Kivu, South Kivu, and Ituri provinces
   - Secondary monitoring of other agricultural regions
   - Detailed analysis of conflict-affected agricultural zones

6. **Data Integration**:
   - Combine satellite data with conflict zone information
   - Integrate with agricultural production data
   - Correlate with food security assessments
