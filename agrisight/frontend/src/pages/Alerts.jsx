import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { alertsAPI } from '../lib/api';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Bell, Check, RefreshCcw } from 'lucide-react';

const Alerts = () => {
  const { data, isLoading, isError, refetch, isFetching } = useQuery({
    queryKey: ['alerts'],
    queryFn: () => alertsAPI.getAlerts(),
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Alerts</h1>
          <p className="text-gray-600 dark:text-gray-400">System notifications and stress warnings</p>
        </div>
        <Button variant="outline" onClick={() => refetch()} disabled={isFetching}>
          <RefreshCcw className="h-4 w-4 mr-2"/>Refresh
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Recent Alerts</CardTitle>
          <CardDescription>Latest system alerts</CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="py-12 text-center text-gray-600 dark:text-gray-400">Loading alerts...</div>
          ) : isError ? (
            <div className="py-12 text-center text-red-600">Failed to load alerts.</div>
          ) : data?.results?.length ? (
            <div className="space-y-3">
              {data.results.map((alert) => (
                <div key={alert.id} className="flex items-start justify-between p-3 rounded-lg bg-gray-50 dark:bg-gray-800">
                  <div className="flex items-start gap-3">
                    <div className="w-8 h-8 rounded-full bg-red-100 dark:bg-red-900/20 flex items-center justify-center">
                      <Bell className="h-4 w-4 text-red-600"/>
                    </div>
                    <div>
                      <p className="font-medium text-gray-900 dark:text-white">{alert.title || 'Alert'}</p>
                      <p className="text-sm text-gray-600 dark:text-gray-400">{alert.message || alert.description}</p>
                      <div className="mt-1 space-x-2">
                        {alert.severity && (
                          <Badge variant="outline">{alert.severity}</Badge>
                        )}
                        {alert.region && (
                          <Badge variant="secondary">{alert.region?.name}</Badge>
                        )}
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Button variant="outline" size="sm"><Check className="h-4 w-4 mr-1"/>Mark read</Button>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="py-12 text-center">
              <div className="mx-auto w-12 h-12 rounded-full bg-gray-100 dark:bg-gray-800 flex items-center justify-center">
                <Bell className="h-6 w-6 text-gray-400"/>
              </div>
              <p className="mt-3 text-gray-900 dark:text-white font-medium">No alerts</p>
              <p className="text-gray-600 dark:text-gray-400">You're all caught up.</p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default Alerts;


