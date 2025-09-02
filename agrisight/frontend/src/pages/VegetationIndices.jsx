import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { ResponsiveContainer, LineChart, Line, CartesianGrid, XAxis, YAxis, Tooltip } from 'recharts';

const sample = [
  { date: '2023-10-01', ndvi: 0.62, evi: 0.55 },
  { date: '2023-10-08', ndvi: 0.58, evi: 0.52 },
  { date: '2023-10-15', ndvi: 0.55, evi: 0.49 },
];

const VegetationIndices = () => {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Vegetation Indices</h1>
      <Card>
        <CardHeader>
          <CardTitle>NDVI / EVI Trends</CardTitle>
          <CardDescription>Aggregated across regions (stub)</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={sample}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis domain={[0, 1]} />
                <Tooltip />
                <Line type="monotone" dataKey="ndvi" stroke="#10b981" strokeWidth={2} />
                <Line type="monotone" dataKey="evi" stroke="#3b82f6" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default VegetationIndices;


