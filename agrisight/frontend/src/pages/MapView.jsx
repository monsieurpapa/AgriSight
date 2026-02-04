import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, GeoJSON, Popup, useMap, LayerGroup, CircleMarker } from 'react-leaflet';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Slider } from '../components/ui/slider';
import { Badge } from '../components/ui/badge';
import { Checkbox } from '../components/ui/checkbox';
import { MapPin, Layers, Satellite, Ruler, Download, AlertTriangle, Activity, Eye, EyeOff, Maximize2, Minimize2 } from 'lucide-react';
import { geospatialAPI, analyticsAPI, satelliteProcessingAPI } from '../lib/api';
import { formatDate, formatVegetationIndex, getVegetationIndexColor, getVegetationIndexLabel } from '../lib/utils';
import 'leaflet/dist/leaflet.css';

// Component to update map bounds when regions change
const MapBoundsUpdater = ({ regions }) => {
  const map = useMap();

  useEffect(() => {
    if (regions && regions.length > 0) {
      const bounds = regions
        .filter(region => region.geometry)
        .map(region => {
          // Convert GeoJSON geometry to Leaflet bounds
          const coords = region.geometry.coordinates[0];
          return coords.map(coord => [coord[1], coord[0]]); // Leaflet expects [lat, lng]
        })
        .flat();

      if (bounds.length > 0) {
        map.fitBounds(bounds, { padding: [20, 20] });
      }
    }
  }, [regions, map]);

  return null;
};

const MapView = () => {
  const [regions, setRegions] = useState([]);
  const [stressEvents, setStressEvents] = useState([]);
  const [selectedRegion, setSelectedRegion] = useState(null);
  const [vegetationData, setVegetationData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [layers, setLayers] = useState({
    ndvi: true,
    evi: false,
    ndwi: false,
    stressEvents: true
  });
  const [opacity, setOpacity] = useState(80);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [baseLayer, setBaseLayer] = useState('osm'); // osm, satellite, terrain

  // Fetch map data
  useEffect(() => {
    const fetchMapData = async () => {
      try {
        setLoading(true);
        setError(null);

        // Fetch regions and stress events in parallel
        const [regionsData, stressData] = await Promise.all([
          geospatialAPI.getRegions(),
          analyticsAPI.getStressEvents({ limit: 100 })
        ]);

        setRegions(regionsData.results || []);
        setStressEvents(stressData.results || []);

        // Set first region as selected by default
        if (regionsData.results && regionsData.results.length > 0) {
          setSelectedRegion(regionsData.results[0]);
        }
      } catch (err) {
        console.error('Failed to fetch map data:', err);
        setError('Failed to load map data. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    fetchMapData();
  }, []);

  // Fetch vegetation data for selected region
  useEffect(() => {
    const fetchVegetationData = async () => {
      if (!selectedRegion) return;

      try {
        const data = await satelliteProcessingAPI.getRegionVegetationData(selectedRegion.id, { days: 30 });
        setVegetationData(data);
      } catch (err) {
        console.warn('Failed to fetch vegetation data:', err);
        setVegetationData(null);
      }
    };

    fetchVegetationData();
  }, [selectedRegion]);

  const getSeverityLevel = (severity) => {
    if (severity == null) {
      return 'low';
    }

    const numericSeverity = Number(severity);
    if (!Number.isNaN(numericSeverity)) {
      if (numericSeverity >= 4) return 'high';
      if (numericSeverity >= 2) return 'medium';
      return 'low';
    }

    const normalized = String(severity).toLowerCase();
    if (normalized === 'high' || normalized === 'medium' || normalized === 'low') {
      return normalized;
    }

    return 'low';
  };

  const getLayerOpacity = () => {
    return Math.max(0.1, Math.min(1, opacity / 100));
  };

  // Get region style based on stress events
  const getRegionStyle = (region) => {
    const layerOpacity = getLayerOpacity();
    const regionStressEvents = stressEvents.filter(event => event.region?.id === region.id);
    const hasHighStress = regionStressEvents.some(event => getSeverityLevel(event.severity) === 'high');
    const hasMediumStress = regionStressEvents.some(event => getSeverityLevel(event.severity) === 'medium');

    if (hasHighStress) {
      return { color: '#ef4444', weight: 2, opacity: 0.9, fillOpacity: Math.min(1, layerOpacity * 0.6) };
    } else if (hasMediumStress) {
      return { color: '#f59e0b', weight: 2, opacity: 0.85, fillOpacity: Math.min(1, layerOpacity * 0.45) };
    } else {
      return { color: '#10b981', weight: 2, opacity: 0.8, fillOpacity: Math.min(1, layerOpacity * 0.3) };
    }
  };

  // Get latest vegetation index for region
  const getLatestVegetationIndex = (regionId, indexType = 'NDVI') => {
    if (!vegetationData || selectedRegion?.id !== regionId) return null;

    const indexData = vegetationData.filter(item => item.index_type === indexType);
    if (indexData.length === 0) return null;

    return indexData.sort((a, b) => new Date(b.date) - new Date(a.date))[0];
  };
  if (loading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Interactive Map</h1>
            <p className="text-gray-600 dark:text-gray-400">Loading satellite overlays and vegetation indices...</p>
          </div>
        </div>
        <div className="h-[520px] w-full bg-gray-200 dark:bg-gray-800 flex items-center justify-center">
          <div className="text-center">
            <Activity className="h-8 w-8 mx-auto text-gray-500 animate-spin"/>
            <p className="mt-2 text-gray-600 dark:text-gray-400">Loading map data...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Interactive Map</h1>
            <p className="text-gray-600 dark:text-gray-400">Satellite overlays and vegetation indices</p>
          </div>
        </div>
        <Card className="border-red-200 bg-red-50 dark:bg-red-900/10">
          <CardContent className="p-6">
            <div className="flex items-center space-x-3">
              <AlertTriangle className="h-6 w-6 text-red-600" />
              <div>
                <h3 className="text-lg font-semibold text-red-800 dark:text-red-200">
                  Error Loading Map
                </h3>
                <p className="text-red-600 dark:text-red-300 mt-1">
                  {error}
                </p>
                <Button
                  variant="outline"
                  size="sm"
                  className="mt-3"
                  onClick={() => window.location.reload()}
                >
                  Retry
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Interactive Map</h1>
          <p className="text-gray-600 dark:text-gray-400">
            {regions.length} regions - {stressEvents.length} stress events - {baseLayer} view
          </p>
        </div>
        <div className="flex gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setIsFullscreen(!isFullscreen)}
          >
            {isFullscreen ? <Minimize2 className="h-4 w-4 mr-2"/> : <Maximize2 className="h-4 w-4 mr-2"/>}
            {isFullscreen ? 'Exit Fullscreen' : 'Fullscreen'}
          </Button>
          <Button variant="outline" size="sm">
            <Ruler className="h-4 w-4 mr-2"/>
            Measure
          </Button>
          <Button size="sm">
            <Download className="h-4 w-4 mr-2"/>
            Export
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        <div className="lg:col-span-3">
          <Card>
            <CardContent className="p-0">
              <div className="h-[520px] w-full">
                <MapContainer
                  center={[0.0, 29.0]} // Center on DRC
                  zoom={8}
                  style={{ height: '100%', width: '100%' }}
                  zoomControl={true}
                >
                  {/* Base Layers */}
                  {baseLayer === 'osm' && (
                    <TileLayer
                      attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                      url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                    />
                  )}
                  {baseLayer === 'satellite' && (
                    <TileLayer
                      attribution='&copy; <a href="https://www.esri.com/">Esri</a> &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community'
                      url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
                    />
                  )}
                  {baseLayer === 'terrain' && (
                    <TileLayer
                      attribution='&copy; <a href="https://www.esri.com/">Esri</a> &mdash; Source: USGS, Esri, TANA, DeLorme, and NPS'
                      url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}"
                    />
                  )}

                  {/* Update map bounds when regions change */}
                  <MapBoundsUpdater regions={regions} />

                  {/* Render regions */}
                  {regions.map((region) => (
                    region.geometry && (
                      <GeoJSON
                        key={region.id}
                        data={region.geometry}
                        style={getRegionStyle(region)}
                        eventHandlers={{
                          click: () => setSelectedRegion(region)
                        }}
                      >
                        <Popup>
                          <div className="p-2">
                            <h3 className="font-semibold text-gray-900">{region.name}</h3>
                            <p className="text-sm text-gray-600">
                              Area: {(region.area_hectares / 100).toFixed(1)} km^2
                            </p>
                            {layers.ndvi && (() => {
                              const latestNDVI = getLatestVegetationIndex(region.id, 'NDVI');
                              return latestNDVI ? (
                                <p className="text-sm text-gray-600">
                                  Latest NDVI: {formatVegetationIndex(latestNDVI.mean_value)}
                                </p>
                              ) : null;
                            })()}
                            {layers.evi && (() => {
                              const latestEVI = getLatestVegetationIndex(region.id, 'EVI');
                              return latestEVI ? (
                                <p className="text-sm text-gray-600">
                                  Latest EVI: {formatVegetationIndex(latestEVI.mean_value)}
                                </p>
                              ) : null;
                            })()}
                            {layers.ndwi && (() => {
                              const latestNDWI = getLatestVegetationIndex(region.id, 'NDWI');
                              return latestNDWI ? (
                                <p className="text-sm text-gray-600">
                                  Latest NDWI: {formatVegetationIndex(latestNDWI.mean_value)}
                                </p>
                              ) : null;
                            })()}
                            {(() => {
                              const regionStressEvents = stressEvents.filter(event => event.region?.id === region.id);
                              return regionStressEvents.length > 0 ? (
                                <div className="mt-2">
                                  <p className="text-sm font-medium text-red-600">
                                    {regionStressEvents.length} stress event{regionStressEvents.length > 1 ? 's' : ''}
                                  </p>
                                </div>
                              ) : null;
                            })()}
                          </div>
                        </Popup>
                      </GeoJSON>
                    )
                  ))}
                  {/* Render stress events with enhanced visualization */}
                  {layers.stressEvents && (
                    <LayerGroup>
                      {stressEvents.map((event) => {
                        // Calculate center point of region for marker placement
                        let centerLat = 0, centerLng = 0;
                        if (event.region?.geometry?.coordinates?.[0]) {
                          const coords = event.region.geometry.coordinates[0];
                          const sum = coords.reduce((acc, coord) => {
                            acc.lat += coord[1];
                            acc.lng += coord[0];
                            return acc;
                          }, { lat: 0, lng: 0 });
                          centerLat = sum.lat / coords.length;
                          centerLng = sum.lng / coords.length;
                        }

                        const severityLevel = getSeverityLevel(event.severity);
                        const severityColor = severityLevel === 'high' ? '#ef4444' :
                                            severityLevel === 'medium' ? '#f59e0b' : '#10b981';
                        const severitySize = severityLevel === 'high' ? 12 :
                                           severityLevel === 'medium' ? 8 : 6;

                        return (
                          <CircleMarker
                            key={`stress-marker-${event.id}`}
                            center={[centerLat, centerLng]}
                            radius={severitySize}
                            pathOptions={{
                              color: severityColor,
                              fillColor: severityColor,
                              fillOpacity: Math.max(0.25, getLayerOpacity()),
                              weight: 2,
                              opacity: 0.9
                            }}
                          >
                            <Popup>
                              <div className="p-3 min-w-[200px]">
                                <div className="flex items-center gap-2 mb-2">
                                  <AlertTriangle className="h-4 w-4 text-red-500" />
                                  <h3 className="font-semibold text-gray-900">Stress Event</h3>
                                </div>
                                <div className="space-y-2 text-sm">
                                  <div>
                                    <span className="font-medium text-gray-700">Type:</span>
                                    <span className="ml-2 text-gray-600">{event.stress_type}</span>
                                  </div>
                                  <div>
                                    <span className="font-medium text-gray-700">Severity:</span>
                                    <Badge
                                      variant="outline"
                                      className={`ml-2 ${
                                        severityLevel === 'high' ? 'border-red-500 text-red-700' :
                                        severityLevel === 'medium' ? 'border-yellow-500 text-yellow-700' :
                                        'border-green-500 text-green-700'
                                      }`}
                                    >
                                      {severityLevel}
                                    </Badge>
                                  </div>
                                  <div>
                                    <span className="font-medium text-gray-700">Region:</span>
                                    <span className="ml-2 text-gray-600">{event.region?.name || 'Unknown'}</span>
                                  </div>
                                  <div>
                                    <span className="font-medium text-gray-700">Detected:</span>
                                    <span className="ml-2 text-gray-600">{formatDate(event.detection_date)}</span>
                                  </div>
                                  {event.affected_area_hectares && (
                                    <div>
                                      <span className="font-medium text-gray-700">Affected Area:</span>
                                      <span className="ml-2 text-gray-600">
                                        {(event.affected_area_hectares / 100).toFixed(1)} km^2
                                      </span>
                                    </div>
                                  )}
                                  {event.description && (
                                    <div>
                                      <span className="font-medium text-gray-700">Description:</span>
                                      <p className="mt-1 text-gray-600 text-xs">{event.description}</p>
                                    </div>
                                  )}
                                </div>
                              </div>
                            </Popup>
                          </CircleMarker>
                        );
                      })}
                    </LayerGroup>
                  )}
                </MapContainer>
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="lg:col-span-1 space-y-6">
          {/* Base Layer Selection */}
          <Card>
            <CardHeader>
              <CardTitle>Base Map</CardTitle>
              <CardDescription>Choose your base layer</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="grid grid-cols-1 gap-2">
                <Button
                  variant={baseLayer === 'osm' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setBaseLayer('osm')}
                  className="justify-start"
                >
                  <MapPin className="h-4 w-4 mr-2" />
                  OpenStreetMap
                </Button>
                <Button
                  variant={baseLayer === 'satellite' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setBaseLayer('satellite')}
                  className="justify-start"
                >
                  <Satellite className="h-4 w-4 mr-2" />
                  Satellite Imagery
                </Button>
                <Button
                  variant={baseLayer === 'terrain' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setBaseLayer('terrain')}
                  className="justify-start"
                >
                  <Layers className="h-4 w-4 mr-2" />
                  Terrain
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Layer Controls */}
          <Card>
            <CardHeader>
              <CardTitle>Data Layers</CardTitle>
              <CardDescription>Toggle vegetation and event overlays</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Vegetation Indices */}
              <div className="space-y-3">
                <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300">Vegetation Indices</h4>
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2 text-sm">
                      <div className="w-3 h-3 rounded-full bg-green-500"></div>
                      NDVI
                    </div>
                    <Checkbox
                      checked={layers.ndvi}
                      onCheckedChange={(checked) => setLayers(prev => ({ ...prev, ndvi: checked }))}
                    />
                  </div>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2 text-sm">
                      <div className="w-3 h-3 rounded-full bg-blue-500"></div>
                      EVI
                    </div>
                    <Checkbox
                      checked={layers.evi}
                      onCheckedChange={(checked) => setLayers(prev => ({ ...prev, evi: checked }))}
                    />
                  </div>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2 text-sm">
                      <div className="w-3 h-3 rounded-full bg-cyan-500"></div>
                      NDWI
                    </div>
                    <Checkbox
                      checked={layers.ndwi}
                      onCheckedChange={(checked) => setLayers(prev => ({ ...prev, ndwi: checked }))}
                    />
                  </div>
                </div>
              </div>

              {/* Events */}
              <div className="space-y-3">
                <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300">Events</h4>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2 text-sm">
                    <AlertTriangle className="h-4 w-4 text-red-500" />
                    Stress Events
                    <Badge variant="secondary" className="text-xs">
                      {stressEvents.length}
                    </Badge>
                  </div>
                  <Checkbox
                    checked={layers.stressEvents}
                    onCheckedChange={(checked) => setLayers(prev => ({ ...prev, stressEvents: checked }))}
                  />
                </div>
              </div>

              {/* Opacity Control */}
              <div className="pt-2 border-t border-gray-200 dark:border-gray-700">
                <div className="flex items-center justify-between mb-2">
                  <p className="text-sm font-medium text-gray-700 dark:text-gray-300">Opacity</p>
                  <span className="text-xs text-gray-500">{opacity}%</span>
                </div>
                <Slider
                  value={[opacity]}
                  onValueChange={(value) => setOpacity(value[0])}
                  max={100}
                  step={5}
                  className="w-full"
                />
              </div>
            </CardContent>
          </Card>
          {/* Map Legend */}
          <Card>
            <CardHeader>
              <CardTitle>Legend</CardTitle>
              <CardDescription>Map symbols and colors</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Stress Event Severity */}
              <div className="space-y-2">
                <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300">Stress Events</h4>
                <div className="space-y-1">
                  <div className="flex items-center gap-2 text-xs">
                    <div className="w-3 h-3 rounded-full bg-red-500"></div>
                    <span>High Severity</span>
                  </div>
                  <div className="flex items-center gap-2 text-xs">
                    <div className="w-2.5 h-2.5 rounded-full bg-yellow-500"></div>
                    <span>Medium Severity</span>
                  </div>
                  <div className="flex items-center gap-2 text-xs">
                    <div className="w-2 h-2 rounded-full bg-green-500"></div>
                    <span>Low Severity</span>
                  </div>
                </div>
              </div>

              {/* Region Health */}
              <div className="space-y-2">
                <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300">Region Health</h4>
                <div className="space-y-1">
                  <div className="flex items-center gap-2 text-xs">
                    <div className="w-3 h-3 border-2 border-green-500 bg-green-100"></div>
                    <span>Healthy</span>
                  </div>
                  <div className="flex items-center gap-2 text-xs">
                    <div className="w-3 h-3 border-2 border-yellow-500 bg-yellow-100"></div>
                    <span>Moderate Stress</span>
                  </div>
                  <div className="flex items-center gap-2 text-xs">
                    <div className="w-3 h-3 border-2 border-red-500 bg-red-100"></div>
                    <span>High Stress</span>
                  </div>
                </div>
              </div>

              {/* Vegetation Indices */}
              <div className="space-y-2">
                <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300">Vegetation Indices</h4>
                <div className="space-y-1">
                  <div className="flex items-center gap-2 text-xs">
                    <div className="w-3 h-1 bg-green-500"></div>
                    <span>NDVI (Vegetation)</span>
                  </div>
                  <div className="flex items-center gap-2 text-xs">
                    <div className="w-3 h-1 bg-blue-500"></div>
                    <span>EVI (Enhanced)</span>
                  </div>
                  <div className="flex items-center gap-2 text-xs">
                    <div className="w-3 h-1 bg-cyan-500"></div>
                    <span>NDWI (Water)</span>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {selectedRegion && (
            <Card>
              <CardHeader>
                <CardTitle>Selected Region</CardTitle>
                <CardDescription>Detailed information</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex items-start gap-2 text-sm">
                    <MapPin className="h-4 w-4 mt-0.5 text-blue-500"/>
                    <div>
                      <p className="font-medium text-gray-900 dark:text-white">{selectedRegion.name}</p>
                      <p className="text-gray-600 dark:text-gray-400">
                        Area: {(selectedRegion.area_hectares / 100).toFixed(1)} km^2
                      </p>
                    </div>
                  </div>

                  {(() => {
                    const indexTypes = [
                      { key: 'ndvi', label: 'NDVI', type: 'NDVI' },
                      { key: 'evi', label: 'EVI', type: 'EVI' },
                      { key: 'ndwi', label: 'NDWI', type: 'NDWI' }
                    ];
                    const activeIndexTypes = indexTypes.filter(item => layers[item.key]);
                    const indexCards = activeIndexTypes.map((item) => {
                      const latest = getLatestVegetationIndex(selectedRegion.id, item.type);
                      if (!latest) return null;

                      return (
                        <div key={item.type} className="p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                          <div className="flex items-center justify-between mb-1">
                            <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                              Latest {item.label}
                            </span>
                            <Badge
                              variant="outline"
                              className={getVegetationIndexColor(latest.mean_value, item.type)}
                            >
                              {getVegetationIndexLabel(latest.mean_value, item.type)}
                            </Badge>
                          </div>
                          <p className="text-lg font-bold text-gray-900 dark:text-white">
                            {formatVegetationIndex(latest.mean_value)}
                          </p>
                          <p className="text-xs text-gray-500 dark:text-gray-400">
                            {formatDate(latest.date)}
                          </p>
                        </div>
                      );
                    }).filter(Boolean);

                    if (activeIndexTypes.length === 0) {
                      return (
                        <div className="p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                          <p className="text-sm text-gray-500 dark:text-gray-400">
                            Enable a vegetation layer to view index data
                          </p>
                        </div>
                      );
                    }

                    return indexCards.length > 0 ? (
                      <div className="space-y-3">
                        {indexCards}
                      </div>
                    ) : (
                      <div className="p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                        <p className="text-sm text-gray-500 dark:text-gray-400">No vegetation data available</p>
                      </div>
                    );
                  })()}

                  {(() => {
                    const regionStressEvents = stressEvents.filter(event => event.region?.id === selectedRegion.id);
                    return regionStressEvents.length > 0 ? (
                      <div className="p-3 bg-red-50 dark:bg-red-900/20 rounded-lg">
                        <div className="flex items-center gap-2 mb-2">
                          <AlertTriangle className="h-4 w-4 text-red-500" />
                          <span className="text-sm font-medium text-red-700 dark:text-red-300">
                            {regionStressEvents.length} stress event{regionStressEvents.length > 1 ? 's' : ''}
                          </span>
                        </div>
                        <div className="space-y-1">
                          {regionStressEvents.slice(0, 3).map((event, index) => (
                            <div key={index} className="text-xs text-red-600 dark:text-red-400">
                              - {event.stress_type} ({getSeverityLevel(event.severity)})
                            </div>
                          ))}
                          {regionStressEvents.length > 3 && (
                            <div className="text-xs text-red-500">
                              +{regionStressEvents.length - 3} more...
                            </div>
                          )}
                        </div>
                      </div>
                    ) : (
                      <div className="p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
                        <div className="flex items-center gap-2">
                          <div className="w-2 h-2 rounded-full bg-green-500"></div>
                          <span className="text-sm text-green-700 dark:text-green-300">No stress events</span>
                        </div>
                      </div>
                    );
                  })()}
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
};

export default MapView;
