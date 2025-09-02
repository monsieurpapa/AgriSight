import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Download, FileDown, ImageDown } from 'lucide-react';

const Exports = () => {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Exports</h1>
          <p className="text-gray-600 dark:text-gray-400">Download data and imagery</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>CSV Data Export</CardTitle>
            <CardDescription>Vegetation indices and region stats</CardDescription>
          </CardHeader>
          <CardContent>
            <Button className="w-full"><FileDown className="h-4 w-4 mr-2"/>Download CSV</Button>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>GeoJSON Export</CardTitle>
            <CardDescription>Region boundaries and attributes</CardDescription>
          </CardHeader>
          <CardContent>
            <Button className="w-full"><Download className="h-4 w-4 mr-2"/>Download GeoJSON</Button>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Imagery Export</CardTitle>
            <CardDescription>Map view snapshot as PNG</CardDescription>
          </CardHeader>
          <CardContent>
            <Button className="w-full"><ImageDown className="h-4 w-4 mr-2"/>Download PNG</Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Exports;


