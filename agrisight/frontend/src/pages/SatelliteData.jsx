import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Satellite, Play, RefreshCcw } from 'lucide-react';
import { satelliteProcessingAPI } from '../lib/api';

const SatelliteData = () => {
  const { data, isLoading, isError, refetch, isFetching } = useQuery({
    queryKey: ['processing-statistics'],
    queryFn: () => satelliteProcessingAPI.getProcessingStatistics(),
    refetchInterval: 60000
  });

  const overview = data?.overview;
  const regionStats = data?.region_statistics || [];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Satellite Data</h1>
          <p className="text-gray-600 dark:text-gray-400">Processing and ingestion status</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => refetch()} disabled={isFetching}>
            <RefreshCcw className={`h-4 w-4 mr-2 ${isFetching ? 'animate-spin' : ''}`}/>Refresh
          </Button>
          <Button variant="outline">
            <Play className="h-4 w-4 mr-2"/>Trigger Processing
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <p className="text-sm text-gray-600 dark:text-gray-400">Active Tasks</p>
            <p className="text-2xl font-bold text-gray-900 dark:text-white">{overview?.active_tasks ?? 0}</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <p className="text-sm text-gray-600 dark:text-gray-400">Images Processed</p>
            <p className="text-2xl font-bold text-gray-900 dark:text-white">{overview?.processed_images ?? 0}</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <p className="text-sm text-gray-600 dark:text-gray-400">Processing %</p>
            <p className="text-2xl font-bold text-gray-900 dark:text-white">
              {overview?.processing_percentage ? overview.processing_percentage.toFixed(1) : 0}%
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <p className="text-sm text-gray-600 dark:text-gray-400">Recent Stress Events</p>
            <p className="text-2xl font-bold text-gray-900 dark:text-white">{overview?.recent_stress_events ?? 0}</p>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Processing Status by Region</CardTitle>
          <CardDescription>Latest processing metrics per region</CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="py-12 text-center text-gray-600 dark:text-gray-400">Loading processing stats...</div>
          ) : isError ? (
            <div className="py-12 text-center text-red-600">Failed to load processing stats.</div>
          ) : regionStats.length > 0 ? (
            <div className="space-y-3">
              {regionStats.map((region) => (
                <div key={region.region_id} className="flex items-center justify-between p-3 rounded-lg bg-gray-50 dark:bg-gray-800">
                  <div>
                    <p className="font-medium text-gray-900 dark:text-white">{region.region_name}</p>
                    <p className="text-xs text-gray-500 dark:text-gray-400">
                      {region.processed_images}/{region.total_images} images processed
                    </p>
                  </div>
                  <div className="text-right text-sm text-gray-600 dark:text-gray-400">
                    {region.stress_events} stress events
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="h-48 rounded-lg bg-gray-100 dark:bg-gray-800 flex items-center justify-center">
              <div className="text-center">
                <Satellite className="h-6 w-6 mx-auto text-gray-500"/>
                <p className="text-gray-600 dark:text-gray-400 mt-2">No processing stats available</p>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default SatelliteData;


