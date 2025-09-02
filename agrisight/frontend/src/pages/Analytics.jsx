import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';

const Analytics = () => {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Analytics</h1>
      <Card>
        <CardHeader>
          <CardTitle>Insights</CardTitle>
          <CardDescription>Predictive analysis (placeholder)</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="h-40 rounded-md bg-gray-100 dark:bg-gray-800 flex items-center justify-center text-gray-500">Coming soon</div>
        </CardContent>
      </Card>
    </div>
  );
};

export default Analytics;


