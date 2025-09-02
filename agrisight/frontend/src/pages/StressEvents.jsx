import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { AlertTriangle } from 'lucide-react';

const StressEvents = () => {
  const items = [
    { id: 1, title: 'Low NDVI detected', region: 'Rutshuru Valley', severity: 'High' },
    { id: 2, title: 'Water stress risk', region: 'Uvira Coastal Plains', severity: 'Medium' },
  ];

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Stress Events</h1>
      <Card>
        <CardHeader>
          <CardTitle>Recent Events</CardTitle>
          <CardDescription>Detected anomalies</CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          {items.map((e) => (
            <div key={e.id} className="flex items-start gap-3 p-3 rounded-lg bg-gray-50 dark:bg-gray-800">
              <div className="w-8 h-8 rounded-full bg-red-100 dark:bg-red-900/20 flex items-center justify-center">
                <AlertTriangle className="h-4 w-4 text-red-600"/>
              </div>
              <div className="flex-1">
                <p className="font-medium text-gray-900 dark:text-white">{e.title}</p>
                <p className="text-sm text-gray-600 dark:text-gray-400">{e.region}</p>
              </div>
              <Badge variant="outline">{e.severity}</Badge>
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  );
};

export default StressEvents;


