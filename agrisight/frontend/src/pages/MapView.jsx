import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, GeoJSON, Popup, useMap } from 'react-leaflet';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Slider } from '../components/ui/slider';
import { Badge } from '../components/ui/badge';
import { MapPin, Layers, Satellite, Ruler, Download, AlertTriangle, Activity } from 'lucide-react';
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

  // Get region style based on stress events
  const getRegionStyle = (region) => {
    const regionStressEvents = stressEvents.filter(event => event.region?.id === region.id);
    const hasHighStress = regionStressEvents.some(event => event.severity === 'high');
    const hasMediumStress = regionStressEvents.some(event => event.severity === 'medium');
    
    if (hasHighStress) {
      return { color: '#ef4444', weight: 2, opacity: 0.8, fillOpacity: 0.3 };
    } else if (hasMediumStress) {
      return { color: '#f59e0b', weight: 2, opacity: 0.8, fillOpacity: 0.3 };
    } else {
      return { color: '#10b981', weight: 2, opacity: 0.8, fillOpacity: 0.2 };
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
            {regions.length} regions • {stressEvents.length} stress events
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline"><Ruler className="h-4 w-4 mr-2"/>Measure</Button>
          <Button><Download className="h-4 w-4 mr-2"/>Export View</Button>
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
                  <TileLayer
                    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                  />
                  
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
                              Area: {(region.area_hectares / 100).toFixed(1)} km²
                            </p>
                            {(() => {
                              const latestNDVI = getLatestVegetationIndex(region.id, 'NDVI');
                              return latestNDVI ? (
                                <p className="text-sm text-gray-600">
                                  Latest NDVI: {formatVegetationIndex(latestNDVI.mean_value)}
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
                  
                  {/* Render stress events */}
                  {layers.stressEvents && stressEvents.map((event) => (
                    event.region?.geometry && (
                      <GeoJSON
                        key={`stress-${event.id}`}
                        data={event.region.geometry}
                        style={{
                          color: event.severity === 'high' ? '#ef4444' : 
                                 event.severity === 'medium' ? '#f59e0b' : '#10b981',
                          weight: 3,
                          opacity: 0.9,
                          fillOpacity: 0.1
                        }}
                      >
                        <Popup>
                          <div className="p-2">
                            <h3 className="font-semibold text-gray-900">Stress Event</h3>
                            <p className="text-sm text-gray-600">
                              Type: {event.stress_type}
                            </p>
                            <p className="text-sm text-gray-600">
                              Severity: <Badge variant="outline" className={getVegetationIndexColor(event.severity === 'high' ? 0.2 : event.severity === 'medium' ? 0.5 : 0.8, 'NDVI')}>
                                {event.severity}
                              </Badge>
                            </p>
                            <p className="text-sm text-gray-600">
                              Detected: {formatDate(event.detection_date)}
                            </p>
                            {event.affected_area_hectares && (
                              <p className="text-sm text-gray-600">
                                Affected Area: {(event.affected_area_hectares / 100).toFixed(1)} km²
                              </p>
                            )}
                          </div>
                        </Popup>
                      </GeoJSON>
                    )
                  ))}
                </MapContainer>
              </div>
            </CardContent>
          </Card>
        </div>
        
        <div className="lg:col-span-1 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Layers</CardTitle>
              <CardDescription>Select overlays</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-sm">
                  <Layers className="h-4 w-4"/> NDVI
                </div>
                <input 
                  type="checkbox" 
                  checked={layers.ndvi}
                  onChange={(e) => setLayers(prev => ({ ...prev, ndvi: e.target.checked }))}
                  className="h-4 w-4"
                />
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-sm">
                  <Layers className="h-4 w-4"/> EVI
                </div>
                <input 
                  type="checkbox" 
                  checked={layers.evi}
                  onChange={(e) => setLayers(prev => ({ ...prev, evi: e.target.checked }))}
                  className="h-4 w-4"
                />
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-sm">
                  <Layers className="h-4 w-4"/> NDWI
                </div>
                <input 
                  type="checkbox" 
                  checked={layers.ndwi}
                  onChange={(e) => setLayers(prev => ({ ...prev, ndwi: e.target.checked }))}
                  className="h-4 w-4"
                />
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-sm">
                  <AlertTriangle className="h-4 w-4"/> Stress Events
                </div>
                <input 
                  type="checkbox" 
                  checked={layers.stressEvents}
                  onChange={(e) => setLayers(prev => ({ ...prev, stressEvents: e.target.checked }))}
                  className="h-4 w-4"
                />
              </div>
              <div className="pt-2">
                <p className="text-xs text-gray-500 mb-2">Opacity</p>
                <Slider 
                  value={[opacity]} 
                  onValueChange={(value) => setOpacity(value[0])}
                  max={100} 
                  step={1}
                />
              </div>
            </CardContent>
          </Card>
          
          {selectedRegion && (
            <Card>
              <CardHeader>
                <CardTitle>Selected Region</CardTitle>
                <CardDescription>Context</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex items-start gap-2 text-sm">
                  <MapPin className="h-4 w-4 mt-0.5"/>
                  <div>
                    <p className="font-medium text-gray-900 dark:text-white">{selectedRegion.name}</p>
                    <p className="text-gray-600 dark:text-gray-400">
                      Area: {(selectedRegion.area_hectares / 100).toFixed(1)} km²
                    </p>
                    {(() => {
                      const latestNDVI = getLatestVegetationIndex(selectedRegion.id, 'NDVI');
                      return latestNDVI ? (
                        <p className="text-gray-600 dark:text-gray-400">
                          Latest NDVI: {formatVegetationIndex(latestNDVI.mean_value)} • {formatDate(latestNDVI.date)}
                        </p>
                      ) : (
                        <p className="text-gray-500 dark:text-gray-500">No vegetation data available</p>
                      );
                    })()}
                    {(() => {
                      const regionStressEvents = stressEvents.filter(event => event.region?.id === selectedRegion.id);
                      return regionStressEvents.length > 0 ? (
                        <div className="mt-2">
                          <p className="text-sm font-medium text-red-600">
                            {regionStressEvents.length} stress event{regionStressEvents.length > 1 ? 's' : ''}
                          </p>
                        </div>
                      ) : null;
                    })()}
                  </div>
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


