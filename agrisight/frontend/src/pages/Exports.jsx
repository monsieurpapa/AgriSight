import React, { useMemo, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Download, FileDown, ImageDown } from 'lucide-react';
import { geospatialAPI } from '../lib/api';

const Exports = () => {
  const [selectedRegion, setSelectedRegion] = useState('all');
  const [selectedIndexType, setSelectedIndexType] = useState('NDVI');

  const { data: regionsData } = useQuery({
    queryKey: ['regions'],
    queryFn: () => geospatialAPI.getRegions()
  });
  const { data: dataQuality } = useQuery({
    queryKey: ['data-quality'],
    queryFn: () => geospatialAPI.getDataQualitySummary()
  });

  const regions = regionsData?.results || regionsData?.features || regionsData || [];

  const regionOptions = useMemo(() => {
    return regions.map((region) => {
      const source = region?.properties || region;
      return {
        id: source.id,
        name: source.name
      };
    }).filter((region) => region.id && region.name);
  }, [regions]);

  const downloadBlob = (blob, filename) => {
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  };

  const handleCsvExport = async () => {
    const params = { index_type: selectedIndexType };
    if (selectedRegion !== 'all') {
      params['satellite_image__region'] = selectedRegion;
    }

    const response = await geospatialAPI.getVegetationIndices(params);
    const items = response?.results || response || [];

    const header = [
      'id',
      'index_type',
      'mean_value',
      'min_value',
      'max_value',
      'std_deviation',
      'raster_path',
      'acquisition_date',
      'satellite_name',
      'region_name'
    ];
    const rows = items.map((item) => {
      const info = item.satellite_image_info || {};
      return [
        item.id,
        item.index_type,
        item.mean_value,
        item.min_value,
        item.max_value,
        item.std_deviation,
        item.raster_path,
        info.acquisition_date,
        info.satellite_name,
        info.region_name
      ];
    });

    const csv = [header, ...rows]
      .map((row) => row.map((value) => `"${String(value ?? '').replace(/"/g, '""')}"`).join(','))
      .join('\n');

    downloadBlob(new Blob([csv], { type: 'text/csv' }), `vegetation_indices_${selectedIndexType}.csv`);
  };

  const handleGeoJsonExport = async () => {
    const response = await geospatialAPI.getRegions();
    if (response?.type === 'FeatureCollection') {
      downloadBlob(new Blob([JSON.stringify(response)], { type: 'application/json' }), 'regions.geojson');
      return;
    }

    const features = response?.results || response?.features || response || [];
    const geojson = {
      type: 'FeatureCollection',
      features: features.map((feature) => {
        if (feature?.type === 'Feature') {
          return feature;
        }
        return {
          type: 'Feature',
          geometry: feature.geometry || null,
          properties: {
            id: feature.id,
            name: feature.name,
            country: feature.country,
            province: feature.province,
            area_hectares: feature.area_hectares
          }
        };
      })
    };

    downloadBlob(new Blob([JSON.stringify(geojson)], { type: 'application/json' }), 'regions.geojson');
  };

  const handleImageryExport = async () => {
    const params = {};
    if (selectedRegion !== 'all') {
      params['region'] = selectedRegion;
    }
    const response = await geospatialAPI.getSatelliteImages(params);
    const items = response?.results || response || [];

    const header = [
      'id',
      'region_name',
      'acquisition_date',
      'satellite_name',
      'cloud_cover_percentage',
      'resolution_meters',
      'is_processed',
      'image_path'
    ];
    const rows = items.map((item) => [
      item.id,
      item.region_name,
      item.acquisition_date,
      item.satellite_name,
      item.cloud_cover_percentage,
      item.resolution_meters,
      item.is_processed,
      item.image_path
    ]);

    const csv = [header, ...rows]
      .map((row) => row.map((value) => `"${String(value ?? '').replace(/"/g, '""')}"`).join(','))
      .join('\n');

    downloadBlob(new Blob([csv], { type: 'text/csv' }), 'satellite_imagery_metadata.csv');
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Exports</h1>
          <p className="text-gray-600 dark:text-gray-400">Download data and imagery</p>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Export Filters</CardTitle>
          <CardDescription>Choose the region and index type for export</CardDescription>
        </CardHeader>
        <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <label className="text-sm text-gray-700 dark:text-gray-300">
            Region
            <select
              className="mt-1 w-full rounded-md border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 px-3 py-2 text-sm"
              value={selectedRegion}
              onChange={(e) => setSelectedRegion(e.target.value)}
            >
              <option value="all">All Regions</option>
              {regionOptions.map((region) => (
                <option key={region.id} value={region.id}>{region.name}</option>
              ))}
            </select>
          </label>
          <label className="text-sm text-gray-700 dark:text-gray-300">
            Vegetation Index
            <select
              className="mt-1 w-full rounded-md border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 px-3 py-2 text-sm"
              value={selectedIndexType}
              onChange={(e) => setSelectedIndexType(e.target.value)}
            >
              {['NDVI', 'EVI', 'NDWI', 'SAVI'].map((index) => (
                <option key={index} value={index}>{index}</option>
              ))}
            </select>
          </label>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>CSV Data Export</CardTitle>
            <CardDescription>Vegetation indices and region stats</CardDescription>
          </CardHeader>
          <CardContent>
            <Button className="w-full" onClick={handleCsvExport}>
              <FileDown className="h-4 w-4 mr-2"/>Download CSV
            </Button>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>GeoJSON Export</CardTitle>
            <CardDescription>Region boundaries and attributes</CardDescription>
          </CardHeader>
          <CardContent>
            <Button className="w-full" onClick={handleGeoJsonExport}>
              <Download className="h-4 w-4 mr-2"/>Download GeoJSON
            </Button>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Imagery Metadata</CardTitle>
            <CardDescription>Satellite imagery metadata in CSV</CardDescription>
          </CardHeader>
          <CardContent>
            <Button className="w-full" onClick={handleImageryExport}>
              <ImageDown className="h-4 w-4 mr-2"/>Download CSV
            </Button>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Data Quality Summary</CardTitle>
          <CardDescription>Quality checks for accessible regions</CardDescription>
        </CardHeader>
        <CardContent className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-3 rounded-lg bg-gray-50 dark:bg-gray-800">
            <p className="text-sm text-gray-600 dark:text-gray-400">Regions</p>
            <p className="text-2xl font-bold text-gray-900 dark:text-white">
              {dataQuality?.regions?.total ?? 0}
            </p>
          </div>
          <div className="p-3 rounded-lg bg-gray-50 dark:bg-gray-800">
            <p className="text-sm text-gray-600 dark:text-gray-400">Satellite Images</p>
            <p className="text-2xl font-bold text-gray-900 dark:text-white">
              {dataQuality?.satellite_images?.total ?? 0}
            </p>
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
              Unprocessed: {dataQuality?.satellite_images?.unprocessed ?? 0}
            </p>
          </div>
          <div className="p-3 rounded-lg bg-gray-50 dark:bg-gray-800">
            <p className="text-sm text-gray-600 dark:text-gray-400">Vegetation Indices</p>
            <p className="text-2xl font-bold text-gray-900 dark:text-white">
              {dataQuality?.vegetation_indices?.total ?? 0}
            </p>
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
              Avg cloud cover: {dataQuality?.satellite_images?.avg_cloud_cover ?? 0}%
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default Exports;
