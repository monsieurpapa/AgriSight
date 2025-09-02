import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Slider } from '../components/ui/slider';
import { MapPin, Layers, Satellite, Ruler, Download } from 'lucide-react';

const MapView = () => {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Interactive Map</h1>
          <p className="text-gray-600 dark:text-gray-400">Satellite overlays and vegetation indices</p>
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
              {/* Placeholder for react-leaflet map to be integrated */}
              <div className="h-[520px] w-full bg-gray-200 dark:bg-gray-800 flex items-center justify-center">
                <div className="text-center">
                  <Satellite className="h-8 w-8 mx-auto text-gray-500"/>
                  <p className="mt-2 text-gray-600 dark:text-gray-400">Map rendering placeholder</p>
                  <p className="text-xs text-gray-500">Integrate react-leaflet with Sentinel overlays</p>
                </div>
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
                <div className="flex items-center gap-2 text-sm"><Layers className="h-4 w-4"/> NDVI</div>
                <input type="checkbox" defaultChecked className="h-4 w-4"/>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-sm"><Layers className="h-4 w-4"/> EVI</div>
                <input type="checkbox" className="h-4 w-4"/>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-sm"><Layers className="h-4 w-4"/> NDWI</div>
                <input type="checkbox" className="h-4 w-4"/>
              </div>
              <div className="pt-2">
                <p className="text-xs text-gray-500 mb-2">Opacity</p>
                <Slider defaultValue={[80]} max={100} step={1}/>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle>Selected Region</CardTitle>
              <CardDescription>Context</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex items-start gap-2 text-sm">
                <MapPin className="h-4 w-4 mt-0.5"/>
                <div>
                  <p className="font-medium text-gray-900 dark:text-white">Goma Agricultural Zone</p>
                  <p className="text-gray-600 dark:text-gray-400">NDVI 0.58 • Last update 2h ago</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default MapView;


