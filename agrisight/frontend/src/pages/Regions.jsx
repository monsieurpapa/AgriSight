import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { regionsAPI } from '../lib/api';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../components/ui/table';
import { Input } from '../components/ui/input';
import { Badge } from '../components/ui/badge';
import { formatArea, getVegetationIndexLabel } from '../lib/utils';
import { MapPin, RefreshCcw, Plus } from 'lucide-react';

const Regions = () => {
  const { data, isLoading, isError, refetch, isFetching } = useQuery({
    queryKey: ['regions'],
    queryFn: () => regionsAPI.getRegions(),
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between gap-4 flex-wrap">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Regions</h1>
          <p className="text-gray-600 dark:text-gray-400">Manage agricultural monitoring regions</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => refetch()} disabled={isFetching}>
            <RefreshCcw className="h-4 w-4 mr-2"/>
            Refresh
          </Button>
          <Button>
            <Plus className="h-4 w-4 mr-2"/>
            Add Region
          </Button>
        </div>
      </div>

      <Card>
        <CardHeader className="gap-2">
          <CardTitle>All Regions</CardTitle>
          <CardDescription>Overview of configured monitoring regions</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between mb-4 gap-3 flex-wrap">
            <Input placeholder="Search regions..." className="max-w-xs"/>
          </div>

          {isLoading ? (
            <div className="py-12 text-center text-gray-600 dark:text-gray-400">Loading regions...</div>
          ) : isError ? (
            <div className="py-12 text-center text-red-600">Failed to load regions.</div>
          ) : data?.results?.length ? (
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Name</TableHead>
                    <TableHead>Area</TableHead>
                    <TableHead>NDVI</TableHead>
                    <TableHead>Updated</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {data.results.map((region) => (
                    <TableRow key={region.id}>
                      <TableCell className="font-medium flex items-center gap-2">
                        <MapPin className="h-4 w-4 text-gray-400"/>
                        {region.name}
                      </TableCell>
                      <TableCell>{formatArea(region.area_km2)}</TableCell>
                      <TableCell>
                        <Badge variant="outline">
                          {getVegetationIndexLabel(region.ndvi, 'NDVI')}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-gray-500">{region.updated_at ? new Date(region.updated_at).toLocaleString() : '—'}</TableCell>
                      <TableCell className="text-right">
                        <Button variant="outline" size="sm">View</Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          ) : (
            <div className="py-12 text-center">
              <div className="mx-auto w-12 h-12 rounded-full bg-gray-100 dark:bg-gray-800 flex items-center justify-center">
                <MapPin className="h-6 w-6 text-gray-400"/>
              </div>
              <p className="mt-3 text-gray-900 dark:text-white font-medium">No regions found</p>
              <p className="text-gray-600 dark:text-gray-400">Create your first monitoring region to get started.</p>
              <Button className="mt-4"><Plus className="h-4 w-4 mr-2"/>Add Region</Button>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default Regions;


