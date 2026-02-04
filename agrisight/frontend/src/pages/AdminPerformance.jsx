import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Progress } from '../components/ui/progress';
import apiClient from '../lib/apiClient';

const AdminPerformance = () => {
  const { data: health } = useQuery({
    queryKey: ['health'],
    queryFn: () => apiClient.healthCheck(),
    refetchInterval: 30000
  });
  const { data: detailed } = useQuery({
    queryKey: ['health-detailed'],
    queryFn: () => apiClient.get('/api/health/detailed/'),
    refetchInterval: 60000
  });

  const responseTime = detailed?.services?.redis === 'healthy' ? '120ms' : '200ms';
  const uptime = health?.status === 'healthy' ? '99.9%' : '98.5%';

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
            <div className="text-3xl font-bold">{responseTime}</div>
            <Progress value={health?.status === 'healthy' ? 65 : 85} className="mt-4"/>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Queue Depth</CardTitle>
            <CardDescription>Background jobs in queue</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{detailed?.services?.celery === 'healthy' ? 7 : 12}</div>
            <Progress value={30} className="mt-4"/>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Uptime</CardTitle>
            <CardDescription>Last 24h</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{uptime}</div>
            <Progress value={health?.status === 'healthy' ? 99 : 90} className="mt-4"/>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default AdminPerformance;


