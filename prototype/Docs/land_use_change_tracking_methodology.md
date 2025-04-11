# Land Use Change Tracking Methodology for AgriSight

## Introduction

This document outlines a comprehensive methodology for tracking land use changes in agricultural areas of the Democratic Republic of Congo (DRC) conflict zones. The methodology leverages satellite-based remote sensing, multispectral analysis, and machine learning techniques to detect, classify, and monitor changes in agricultural land use patterns over time. This approach is specifically designed to address the unique challenges of monitoring conflict-affected regions where ground access is limited or impossible.

## 1. Methodological Framework

### 1.1 Hybrid Change Detection Approach

The AgriSight land use change tracking methodology employs a hybrid approach that combines the strengths of multiple change detection techniques:

1. **Time Series Analysis**: Continuous monitoring of pixel trajectories over time using harmonic regression models to detect abrupt and gradual changes in agricultural patterns.

2. **Post-Classification Comparison**: Independent classification of images from different time periods followed by a comparison to identify changes between classifications.

3. **Direct Multi-Date Classification**: Direct classification of multi-temporal image stacks to identify change patterns.

This hybrid approach provides redundancy and cross-validation, which is particularly important in conflict zones where data quality may be compromised by various factors.

### 1.2 Temporal Analysis Framework

The temporal framework is structured to capture both seasonal variations and conflict-induced changes:

1. **Baseline Period**: Pre-conflict or stable period imagery (minimum 1 year) to establish normal agricultural patterns and seasonal variations.

2. **Monitoring Period**: Continuous monitoring during conflict periods with analysis at multiple temporal scales:
   - Short-term (bi-weekly): For rapid detection of sudden changes
   - Medium-term (monthly): For tracking evolving patterns
   - Long-term (seasonal/annual): For comprehensive change assessment

3. **Change Verification Period**: Post-event imagery to verify persistence of changes and distinguish between temporary and permanent alterations.

## 2. Data Sources and Preprocessing

### 2.1 Primary Satellite Data Sources

1. **Sentinel-2**: 10m resolution, 5-day revisit time, 13 spectral bands
   - Primary data source for regular monitoring
   - Suitable for detecting field-level changes

2. **Landsat 8/9**: 30m resolution, 16-day revisit time, 11 spectral bands
   - Historical baseline data (archive dating back to 1980s)
   - Thermal bands for additional analysis

3. **PlanetScope**: 3-5m resolution, daily revisit
   - For detailed analysis of critical areas
   - Used when higher spatial resolution is required

4. **SAR Data (Sentinel-1)**: 10-20m resolution, 6-day revisit
   - All-weather, day-night imaging capability
   - Critical for monitoring during cloud cover and rainy seasons

### 2.2 Data Preprocessing Pipeline

1. **Atmospheric Correction**: Surface reflectance calibration using SMAC or Sen2Cor

2. **Cloud and Shadow Masking**: 
   - Implementation of Mountainous Fmask (MFmask) algorithm for automated cloud and shadow detection
   - Additional quality filtering based on metadata

3. **Geometric Correction**: Co-registration of multi-temporal images with sub-pixel accuracy

4. **Temporal Compositing**: Creation of cloud-free composites using:
   - Best-available-pixel approach for clear observations
   - Weighted averaging for partially cloudy periods
   - Gap-filling using temporal interpolation

5. **Spectral Index Calculation**: Computation of vegetation indices (NDVI, EVI, NDWI, SAVI) for each time step

## 3. Change Detection Algorithms

### 3.1 Continuous Change Detection and Classification (CCDC)

The CCDC algorithm will be implemented to detect abrupt changes while accounting for seasonal variations:

1. **Harmonic Regression Modeling**: Fitting seasonal harmonic curves to time series data for each pixel
   - Six harmonic components to capture seasonal cycles
   - RMSE thresholds calibrated for DRC agricultural systems

2. **Break Detection**: Identification of points where pixel values deviate significantly from the modeled trajectory
   - Consecutive observation test to reduce false positives
   - Magnitude thresholds adapted to different crop types

3. **Change Characterization**: Classification of detected breaks by:
   - Timing (date of change)
   - Magnitude (severity of change)
   - Direction (increase or decrease in vegetation)
   - Duration (temporary vs. persistent)

### 3.2 LandTrendr Segmentation

LandTrendr will be used to identify gradual changes and long-term trends:

1. **Temporal Segmentation**: Fitting of piecewise linear models to annual time series
   - Vertex identification to detect turning points
   - Segment fitting with optimized parameters for agricultural landscapes

2. **Trend Analysis**: Characterization of segments by:
   - Slope (rate of change)
   - Duration (length of segment)
   - Magnitude (total change over segment)

3. **Disturbance Mapping**: Identification of negative changes exceeding thresholds calibrated for conflict-induced abandonment

### 3.3 Post-Classification Change Detection

A robust post-classification approach will be implemented as a complementary method:

1. **Independent Classification**: Random Forest classification of images from different time periods
   - Training data stratified by agricultural system and region
   - Inclusion of spectral, textural, and contextual features

2. **Classification Refinement**: Application of spatial and temporal filters to reduce noise
   - Majority filtering to remove isolated pixels
   - Temporal consistency checks to eliminate spurious changes

3. **Change Matrix Analysis**: Generation of from-to change matrices to quantify transitions between land use classes
   - Calculation of net and gross change statistics
   - Identification of dominant change trajectories

## 4. Agricultural Abandonment Metrics

### 4.1 Spectral Indicators of Abandonment

1. **Vegetation Index Trajectories**: Analysis of temporal patterns in vegetation indices
   - Decrease followed by stabilization at lower levels
   - Loss of seasonal amplitude in cropping cycles
   - Increased heterogeneity in spatial patterns

2. **Textural Changes**: Quantification of changes in spatial heterogeneity
   - Gray-level co-occurrence matrix (GLCM) metrics
   - Fractal dimension analysis
   - Edge density and fragmentation indices

3. **Phenological Shifts**: Detection of changes in seasonal growing patterns
   - Loss of distinct green-up and senescence periods
   - Altered timing of peak greenness
   - Reduced amplitude of seasonal cycles

### 4.2 Classification of Abandonment Types

1. **Recent Abandonment**: Fields showing abrupt cessation of agricultural activities
   - Characterized by initial decrease in vegetation indices
   - Followed by irregular regrowth patterns

2. **Long-term Abandonment**: Previously cultivated areas showing signs of natural succession
   - Gradual increase in vegetation indices
   - Reduced seasonality
   - Increased spatial heterogeneity

3. **Partial Abandonment**: Fields with reduced management intensity
   - Patchy spatial patterns
   - Maintained but reduced seasonal cycles
   - Intermediate vegetation index values

### 4.3 Quantitative Metrics

1. **Abandonment Rate**: Percentage of agricultural land abandoned per time period
   - Calculated at multiple scales (field, community, region)
   - Stratified by crop type and farming system

2. **Abandonment Duration**: Length of time land remains abandoned
   - Short-term (< 1 year)
   - Medium-term (1-3 years)
   - Long-term (> 3 years)

3. **Spatial Pattern Metrics**: Characterization of the spatial distribution of abandonment
   - Clustering indices
   - Distance to conflict events
   - Proximity to settlements and infrastructure

## 5. Conflict vs. Climate Impact Differentiation

### 5.1 Spatial Correlation Analysis

1. **Proximity Analysis**: Correlation of change patterns with:
   - Distance to conflict events (from ACLED database)
   - Distance to military installations or checkpoints
   - Proximity to contested territories

2. **Accessibility Modeling**: Analysis of changes in relation to:
   - Distance to roads and settlements
   - Terrain constraints (slope, rivers)
   - Security-related movement restrictions

3. **Pattern Recognition**: Identification of characteristic spatial patterns:
   - Linear features along conflict lines
   - Radial patterns around contested settlements
   - Fragmented patterns in disputed territories

### 5.2 Temporal Correlation Analysis

1. **Event Synchronization**: Correlation of change timing with:
   - Documented conflict events
   - Population displacement data
   - Security incidents

2. **Climate Anomaly Filtering**: Separation of climate-induced changes using:
   - Precipitation anomaly data
   - Temperature deviation patterns
   - Drought indices (SPEI, SPI)

3. **Change Trajectory Analysis**: Differentiation based on temporal characteristics:
   - Conflict: Abrupt changes with irregular recovery
   - Climate: Gradual changes with regional consistency
   - Combined: Complex patterns requiring decomposition

### 5.3 Contextual Variables Integration

1. **Socioeconomic Factors**: Incorporation of data on:
   - Population density and displacement
   - Market access and economic activity
   - Ethnic composition and land tenure

2. **Agricultural System Vulnerability**: Assessment of differential impacts based on:
   - Crop types and farming systems
   - Irrigation dependency
   - Labor requirements

3. **Historical Context**: Analysis in relation to:
   - Pre-existing land use trends
   - Historical conflict patterns
   - Traditional agricultural practices

## 6. Validation Methodology

### 6.1 Statistical Validation

1. **Accuracy Assessment**: Rigorous validation using:
   - Stratified random sampling
   - Confusion matrices for change/no-change
   - User's and producer's accuracies for change classes

2. **Area Estimation**: Bias-corrected area estimates following Olofsson et al. (2014) methodology
   - Calculation of confidence intervals
   - Error-adjusted area estimates
   - Uncertainty reporting for all change metrics

3. **Sensitivity Analysis**: Testing of parameter sensitivity for:
   - Change detection thresholds
   - Temporal window sizes
   - Classification parameters

### 6.2 Cross-Validation with Alternative Data Sources

1. **High-Resolution Imagery**: Validation using:
   - Commercial high-resolution imagery (when available)
   - Drone imagery from secure areas
   - Historical aerial photographs

2. **Field Reports**: Correlation with:
   - NGO and humanitarian organization reports
   - UN agency assessments
   - Journalist accounts and media reports

3. **Local Knowledge Integration**: Validation through:
   - Structured interviews with displaced farmers
   - Participatory mapping with local experts
   - Integration of indigenous knowledge

### 6.3 Temporal Consistency Checks

1. **Logical Sequence Verification**: Checking for logical inconsistencies in change sequences
   - Impossible transitions (e.g., built-up to forest in short periods)
   - Unrealistic rates of change
   - Temporal discontinuities

2. **Trajectory Analysis**: Verification of complete pixel histories
   - Identification of anomalous trajectories
   - Filtering of noise and artifacts
   - Consistency with known agricultural cycles

3. **Independent Method Comparison**: Cross-validation between:
   - CCDC and LandTrendr results
   - Post-classification and direct change detection
   - Different sensor combinations

## 7. Implementation Strategy

### 7.1 Processing Platform

1. **Google Earth Engine**: Primary platform for large-scale processing
   - Access to full Landsat and Sentinel archives
   - Cloud-based computation for time series analysis
   - Implementation of CCDC and LandTrendr algorithms

2. **Local Processing**: Supplementary analysis using:
   - QGIS and custom Python scripts
   - Open-source libraries (scikit-learn, rasterio, geopandas)
   - Specialized software for advanced analysis

3. **Data Management**: Structured approach for:
   - Version control of datasets and algorithms
   - Metadata documentation
   - Result archiving and sharing

### 7.2 Operational Workflow

1. **Initial Setup**: Establishment of baseline conditions
   - Historical analysis (pre-conflict)
   - Land use classification
   - Agricultural system mapping

2. **Regular Monitoring**: Continuous change detection
   - Bi-weekly updates for active conflict zones
   - Monthly updates for all agricultural areas
   - Quarterly comprehensive assessments

3. **Alert System**: Rapid detection of significant changes
   - Automated identification of abandonment hotspots
   - Prioritization of areas for detailed analysis
   - Notification system for critical changes

### 7.3 Adaptation and Refinement

1. **Iterative Improvement**: Continuous refinement based on:
   - Validation results
   - New methodological developments
   - Changing conflict dynamics

2. **Regional Calibration**: Parameter adjustment for:
   - Different agricultural systems
   - Varying ecological zones
   - Specific conflict contexts

3. **Knowledge Transfer**: Documentation and training for:
   - Local partners and stakeholders
   - Humanitarian organizations
   - Government agencies

## 8. Output Products

### 8.1 Change Maps and Statistics

1. **Change Type Maps**: Spatial representation of:
   - Agricultural abandonment
   - Land use conversions
   - Cultivation intensity changes

2. **Temporal Dynamics**: Visualization of:
   - Change timing
   - Duration of abandonment
   - Recovery patterns

3. **Quantitative Metrics**: Regular reporting of:
   - Area statistics with confidence intervals
   - Change rates by region and crop type
   - Trend analysis and projections

### 8.2 Analytical Reports

1. **Conflict Impact Assessment**: Analysis of:
   - Spatial correlation with conflict events
   - Temporal patterns related to conflict intensity
   - Differential impacts by agricultural system

2. **Food Security Implications**: Evaluation of:
   - Production capacity losses
   - Market access disruptions
   - Resilience factors and vulnerabilities

3. **Recovery Potential**: Assessment of:
   - Reversibility of observed changes
   - Rehabilitation requirements
   - Priority areas for intervention

### 8.3 Interactive Dashboard

1. **Web-Based Interface**: Development of:
   - Interactive maps with temporal sliders
   - Customizable analytics
   - Data download capabilities

2. **Alert System**: Implementation of:
   - Real-time monitoring of critical areas
   - Automated detection of significant changes
   - Notification system for stakeholders

3. **Decision Support Tools**: Creation of:
   - Scenario modeling capabilities
   - Intervention planning aids
   - Impact assessment frameworks

## Conclusion

This methodology provides a comprehensive framework for tracking land use changes in agricultural areas of DRC conflict zones. By combining multiple change detection approaches, integrating various data sources, and implementing rigorous validation procedures, the AgriSight project will deliver reliable and actionable information on agricultural abandonment and land use changes. This information will support evidence-based decision-making for food security interventions, humanitarian assistance, and long-term agricultural resilience in conflict-affected regions.
