# Multispectral Imagery Techniques for Agricultural Monitoring in the DRC

## Vegetation Indices for Crop Health Assessment

### 1. NDVI (Normalized Difference Vegetation Index)
- **Formula**: (NIR - Red) / (NIR + Red)
- **Range**: -1 to +1 (typically 0.2 to 0.8 for vegetation)
- **Applications**: 
  - Most common index in agriculture
  - Characterizes vegetation density
  - Assesses germination, growth, presence of weeds or diseases
  - Predicts field productivity
- **Limitations**:
  - Can become saturated in areas with high leaf area index (LAI)
  - Moderately sensitive to soil background and atmospheric effects
  - Shows nonlinear, heteroskedastic relation to actual vegetation fraction
- **Relevance for DRC**: Good baseline index for general crop monitoring, but may have limitations in dense vegetation areas common in tropical regions

### 2. EVI (Enhanced Vegetation Index)
- **Formula**: 2.5 * [(NIR - Red) / (NIR + 6*Red - 7.5*Blue + 1)]
- **Range**: 0 to 1 for vegetation pixels
- **Applications**:
  - Developed to improve NDVI in areas with high leaf area index
  - Uses blue reflection to correct background soil signals
  - Reduces atmospheric effects including aerosol scattering
  - Assesses crop development variability in both dense and sparse vegetation
- **Limitations**:
  - Requires blue band, which is not available on all sensors
  - More complex calculation than NDVI
- **Relevance for DRC**: Excellent for monitoring crops in the varied vegetation densities of DRC, especially in humid tropical regions where NDVI may saturate

### 3. EVI2 (Two-band Enhanced Vegetation Index)
- **Formula**: 2.5 * [(NIR - Red) / (NIR + 2.4*Red + 1)]
- **Applications**:
  - Alternative to EVI when blue band is not available
  - Shows strong correlation with EVI (ρ > 0.99)
  - More closely approximates a 1:1 relationship with vegetation fraction
- **Relevance for DRC**: Good alternative when using sensors without blue band capability

### 4. GNDVI (Green Normalized Difference Vegetation Index)
- **Formula**: (NIR - Green) / (NIR + Green)
- **Applications**:
  - Similar to NDVI but uses green spectrum (0.54-0.57 μm) instead of red
  - More sensitive to chlorophyll concentration than NDVI
  - Used for assessing moisture content and nitrogen concentration
  - Effective for depressed and aged vegetation
- **Relevance for DRC**: Valuable for monitoring nutrient stress in crops, particularly in areas with nitrogen deficiency

### 5. CVI (Chlorophyll Vegetation Index)
- **Applications**:
  - Increased sensitivity to chlorophyll content in leaf cover
  - Used from beginning to middle of crop growth cycle
  - Effective across wide range of soils and sowing conditions
  - Normalizes various LAI values through red and green colors
- **Relevance for DRC**: Useful for early detection of crop stress before visible symptoms appear

### 6. NIRv (Near-Infrared Reflectance of Vegetation)
- **Applications**:
  - Shows strong linear relationship with vegetation fraction (ρ > 0.94)
  - Strongly correlated with DVI
- **Relevance for DRC**: Potential alternative index for vegetation monitoring

### 7. DVI (Difference Vegetation Index)
- **Formula**: NIR - Red
- **Applications**:
  - Simple calculation
  - Shows strong linear relationship with vegetation fraction
- **Relevance for DRC**: Simple but effective index for basic vegetation monitoring

## Soil Moisture and Water Stress Detection

### 1. NDWI (Normalized Difference Water Index)
- **Formula**: (NIR - SWIR) / (NIR + SWIR) or (Green - NIR) / (Green + NIR)
- **Applications**:
  - Measures vegetation water content
  - Correlates significantly with soil moisture across different land uses
  - Effective for drought monitoring
- **Relevance for DRC**: Critical for monitoring agricultural drought in conflict zones where water access may be compromised

### 2. PDI (Perpendicular Drought Index)
- **Applications**:
  - Effective for soil moisture estimation on bare soil
  - Good correlation with in-situ measurements
- **Relevance for DRC**: Useful for monitoring recently planted or harvested fields

### 3. SAVI (Soil-Adjusted Vegetation Index)
- **Formula**: [(NIR - Red) / (NIR + Red + L)] * (1 + L), where L is a soil brightness correction factor
- **Applications**:
  - Minimizes soil brightness influences
  - Useful in areas with low vegetation cover and exposed soil
- **Relevance for DRC**: Valuable in areas with sparse vegetation or during early growth stages

### 4. Thermal Indices
- **Applications**:
  - Crop Water Stress Index (CWSI)
  - Temperature Vegetation Dryness Index (TVDI)
  - Detect plant water stress through canopy temperature
- **Limitations**:
  - Require thermal infrared sensors
  - More complex to implement
- **Relevance for DRC**: Advanced option for detailed water stress monitoring if thermal data is available

## Land Use Classification Techniques

### 1. Supervised Classification
- **Methods**: Maximum Likelihood, Support Vector Machine, Random Forest
- **Applications**:
  - Identifying crop types
  - Mapping agricultural areas vs. non-agricultural areas
  - Detecting land use changes
- **Relevance for DRC**: Essential for mapping agricultural areas in conflict zones and monitoring changes over time

### 2. Unsupervised Classification
- **Methods**: K-means, ISODATA
- **Applications**:
  - Initial land cover assessment
  - Identifying natural clusters in the data
- **Relevance for DRC**: Useful for preliminary assessment when ground truth data is limited

### 3. Object-Based Image Analysis (OBIA)
- **Applications**:
  - Segmentation of fields and agricultural plots
  - Improved classification in heterogeneous landscapes
- **Relevance for DRC**: Valuable for the fragmented agricultural landscape of DRC

## Multitemporal Analysis Techniques

### 1. Change Detection
- **Methods**: Image differencing, post-classification comparison
- **Applications**:
  - Monitoring crop growth stages
  - Detecting agricultural expansion/contraction
  - Identifying abandoned fields in conflict areas
- **Relevance for DRC**: Critical for tracking the impact of conflict on agricultural activities

### 2. Time Series Analysis
- **Methods**: Harmonic analysis, trend analysis
- **Applications**:
  - Monitoring seasonal patterns
  - Detecting anomalies in crop development
  - Assessing long-term changes in agricultural productivity
- **Relevance for DRC**: Essential for distinguishing between seasonal changes and conflict-induced disruptions

## Resolution Considerations for DRC

### 1. Spatial Resolution
- **High Resolution (< 10m)**:
  - Sentinel-2 (10m): Good for field-level monitoring
  - Commercial satellites (0.5-5m): Detailed analysis of specific areas
  - UAV imagery (cm-scale): Targeted monitoring of critical areas
- **Medium Resolution (10-100m)**:
  - Landsat 8 (30m): Historical analysis and broader patterns
- **Relevance for DRC**: 10m resolution (Sentinel-2) provides a good balance for monitoring smallholder agriculture in DRC

### 2. Temporal Resolution
- **High Frequency (Daily-Weekly)**:
  - Essential for capturing rapid changes during growing season
  - Critical for timely intervention in stress conditions
- **Medium Frequency (Bi-weekly-Monthly)**:
  - Sufficient for monitoring general crop development
- **Relevance for DRC**: 3-5 day revisit time of Sentinel-2 is appropriate for monitoring agricultural areas in conflict zones

### 3. Spectral Resolution
- **Multispectral**:
  - Sufficient for standard vegetation indices
  - Widely available and cost-effective
- **Hyperspectral**:
  - Provides detailed spectral information
  - Better for specific stress detection
  - Limited availability and higher cost
- **Relevance for DRC**: Multispectral imagery is practical and sufficient for the AgriSight project

## Implementation Recommendations for AgriSight

1. **Primary Indices for Crop Health Monitoring**:
   - EVI: Best overall performance in tropical environments with varied vegetation density
   - NDVI: Good baseline index for general vegetation monitoring
   - GNDVI: Complementary index for chlorophyll and nitrogen assessment

2. **Water Stress Monitoring**:
   - NDWI: Primary index for vegetation water content
   - SAVI: For areas with sparse vegetation or exposed soil

3. **Multitemporal Analysis Approach**:
   - Establish baseline conditions using historical imagery
   - Implement regular monitoring during growing seasons
   - Conduct change detection analysis to identify anomalies

4. **Resolution Strategy**:
   - Primary monitoring: Sentinel-2 (10m, 3-5 day revisit)
   - Historical analysis: Landsat 8 (30m, 16-day revisit)
   - Detailed assessment of critical areas: Commercial high-resolution imagery

5. **Land Use Classification**:
   - Initial mapping using supervised classification
   - Regular updates to track changes in agricultural areas
   - Integration with conflict zone information

6. **Challenges and Considerations**:
   - Cloud cover in tropical regions may limit optical imagery availability
   - Conflict zones may have limited ground truth data
   - Small, fragmented agricultural plots may require higher resolution imagery
   - Seasonal variations must be distinguished from conflict-induced changes
