import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Progress } from '../components/ui/progress';

const AdminPerformance = () => {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Performance</h1>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>API Latency</CardTitle>
            <CardDescription>p95 response time</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">320ms</div>
            <Progress value={65} className="mt-4"/>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Queue Depth</CardTitle>
            <CardDescription>Background jobs in queue</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">7</div>
            <Progress value={30} className="mt-4"/>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Uptime</CardTitle>
            <CardDescription>Last 24h</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">99.9%</div>
            <Progress value={99} className="mt-4"/>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default AdminPerformance;


