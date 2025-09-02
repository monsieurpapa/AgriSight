import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { organizationsAPI } from '../lib/api';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../components/ui/table';
import { Users, Plus, RefreshCcw } from 'lucide-react';

const Organizations = () => {
  const { data, isLoading, isError, refetch, isFetching } = useQuery({
    queryKey: ['organizations'],
    queryFn: () => organizationsAPI.getOrganizations(),
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Organizations</h1>
          <p className="text-gray-600 dark:text-gray-400">Manage tenant organizations</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => refetch()} disabled={isFetching}>
            <RefreshCcw className="h-4 w-4 mr-2"/>Refresh
          </Button>
          <Button><Plus className="h-4 w-4 mr-2"/>Add Organization</Button>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>All Organizations</CardTitle>
          <CardDescription>Multi-tenant setup</CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="py-12 text-center text-gray-600 dark:text-gray-400">Loading...</div>
          ) : isError ? (
            <div className="py-12 text-center text-red-600">Failed to load.</div>
          ) : data?.results?.length ? (
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Name</TableHead>
                    <TableHead>Type</TableHead>
                    <TableHead>Users</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {data.results.map((org) => (
                    <TableRow key={org.id}>
                      <TableCell className="font-medium flex items-center gap-2">
                        <Users className="h-4 w-4 text-gray-400"/>
                        {org.name}
                      </TableCell>
                      <TableCell>{org.organization_type || '—'}</TableCell>
                      <TableCell>{org.user_count ?? '—'}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          ) : (
            <div className="py-12 text-center text-gray-600 dark:text-gray-400">No organizations.</div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default Organizations;


