import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Satellite, Play, RefreshCcw } from 'lucide-react';

const SatelliteData = () => {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Satellite Data</h1>
          <p className="text-gray-600 dark:text-gray-400">Processing and ingestion status</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline"><RefreshCcw className="h-4 w-4 mr-2"/>Refresh</Button>
          <Button><Play className="h-4 w-4 mr-2"/>Trigger Processing</Button>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Recent Imagery</CardTitle>
          <CardDescription>Latest Sentinel scenes</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="h-48 rounded-lg bg-gray-100 dark:bg-gray-800 flex items-center justify-center">
            <div className="text-center">
              <Satellite className="h-6 w-6 mx-auto text-gray-500"/>
              <p className="text-gray-600 dark:text-gray-400 mt-2">No imagery loaded (stub)</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default SatelliteData;


