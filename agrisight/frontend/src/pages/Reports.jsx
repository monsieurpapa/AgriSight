import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { reportsAPI } from '../lib/api';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../components/ui/table';
import { FileText, Download, Plus, RefreshCcw } from 'lucide-react';

const Reports = () => {
  const { data, isLoading, isError, refetch, isFetching } = useQuery({
    queryKey: ['reports'],
    queryFn: () => reportsAPI.getReports(),
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Reports</h1>
          <p className="text-gray-600 dark:text-gray-400">Generate and download monitoring reports</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => refetch()} disabled={isFetching}>
            <RefreshCcw className="h-4 w-4 mr-2"/>Refresh
          </Button>
          <Button>
            <Plus className="h-4 w-4 mr-2"/>Generate Report
          </Button>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Generated Reports</CardTitle>
          <CardDescription>List of available reports</CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="py-12 text-center text-gray-600 dark:text-gray-400">Loading reports...</div>
          ) : isError ? (
            <div className="py-12 text-center text-red-600">Failed to load reports.</div>
          ) : data?.results?.length ? (
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Title</TableHead>
                    <TableHead>Type</TableHead>
                    <TableHead>Created</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {data.results.map((report) => (
                    <TableRow key={report.id}>
                      <TableCell className="font-medium flex items-center gap-2">
                        <FileText className="h-4 w-4 text-gray-400"/>
                        {report.title || `Report #${report.id}`}
                      </TableCell>
                      <TableCell>{report.type || 'General'}</TableCell>
                      <TableCell>{report.created_at ? new Date(report.created_at).toLocaleString() : '—'}</TableCell>
                      <TableCell className="text-right">
                        <Button variant="outline" size="sm">
                          <Download className="h-4 w-4 mr-1"/>Download
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          ) : (
            <div className="py-12 text-center">
              <div className="mx-auto w-12 h-12 rounded-full bg-gray-100 dark:bg-gray-800 flex items-center justify-center">
                <FileText className="h-6 w-6 text-gray-400"/>
              </div>
              <p className="mt-3 text-gray-900 dark:text-white font-medium">No reports available</p>
              <p className="text-gray-600 dark:text-gray-400">Generate a report to see it listed here.</p>
              <Button className="mt-4"><Plus className="h-4 w-4 mr-2"/>Generate Report</Button>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default Reports;


