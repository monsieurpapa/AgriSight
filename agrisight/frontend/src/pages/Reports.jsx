import React, { useMemo, useState } from 'react';
import { useMutation, useQuery } from '@tanstack/react-query';
import { geospatialAPI, organizationsAPI, reportsAPI } from '../lib/api';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../components/ui/table';
import { FileText, Download, Plus, RefreshCcw } from 'lucide-react';

const Reports = () => {
  const { data, isLoading, isError, refetch, isFetching } = useQuery({
    queryKey: ['reports'],
    queryFn: () => reportsAPI.getReports(),
  });
  const { data: regionsData } = useQuery({
    queryKey: ['regions'],
    queryFn: () => geospatialAPI.getRegions()
  });
  const { data: orgData } = useQuery({
    queryKey: ['current-organization'],
    queryFn: () => organizationsAPI.getCurrentOrganization()
  });
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    title: '',
    report_type: 'stress',
    time_period_start: '',
    time_period_end: '',
    regions: []
  });
  const [formError, setFormError] = useState(null);

  const regions = regionsData?.results || [];
  const organizationId = orgData?.id;

  const reportTypes = useMemo(() => ([
    { value: 'stress', label: 'Agricultural Stress' },
    { value: 'crop_health', label: 'Crop Health' },
    { value: 'water', label: 'Water Resources' },
    { value: 'conflict_impact', label: 'Conflict Impact' },
    { value: 'custom', label: 'Custom Analysis' }
  ]), []);

  const createReport = useMutation({
    mutationFn: (payload) => reportsAPI.createReport(payload),
    onSuccess: () => {
      setFormData({
        title: '',
        report_type: 'stress',
        time_period_start: '',
        time_period_end: '',
        regions: []
      });
      setFormError(null);
      setShowForm(false);
      refetch();
    },
    onError: () => {
      setFormError('Failed to generate report. Please check required fields and try again.');
    }
  });

  const toggleRegion = (regionId) => {
    setFormData((prev) => {
      const exists = prev.regions.includes(regionId);
      return {
        ...prev,
        regions: exists ? prev.regions.filter((id) => id !== regionId) : [...prev.regions, regionId]
      };
    });
  };

  const handleCreate = () => {
    if (!organizationId) {
      setFormError('Organization is required to generate reports.');
      return;
    }
    if (!formData.title || !formData.time_period_start || !formData.time_period_end || formData.regions.length === 0) {
      setFormError('Title, time period, and at least one region are required.');
      return;
    }
    const payload = {
      title: formData.title,
      organization: organizationId,
      regions: formData.regions,
      report_type: formData.report_type,
      time_period_start: formData.time_period_start,
      time_period_end: formData.time_period_end,
      content: { generated_at: new Date().toISOString(), notes: 'Generated from UI' },
      file_path: `reports/${Date.now()}.json`
    };
    createReport.mutate(payload);
  };

  const handleDownload = async (reportId) => {
    try {
      await reportsAPI.downloadReport(reportId);
    } catch (err) {
      console.error('Failed to download report', err);
    }
  };

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
          <Button onClick={() => setShowForm((prev) => !prev)}>
            <Plus className="h-4 w-4 mr-2"/>Generate Report
          </Button>
        </div>
      </div>

      {showForm && (
        <Card>
          <CardHeader>
            <CardTitle>Generate Report</CardTitle>
            <CardDescription>Define report parameters and generate a new report.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {formError && (
              <div className="text-sm text-red-600">{formError}</div>
            )}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <label className="text-sm text-gray-700 dark:text-gray-300">
                Title
                <input
                  type="text"
                  className="mt-1 w-full rounded-md border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 px-3 py-2 text-sm"
                  value={formData.title}
                  onChange={(e) => setFormData((prev) => ({ ...prev, title: e.target.value }))}
                  placeholder="Monthly stress overview"
                />
              </label>
              <label className="text-sm text-gray-700 dark:text-gray-300">
                Report Type
                <select
                  className="mt-1 w-full rounded-md border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 px-3 py-2 text-sm"
                  value={formData.report_type}
                  onChange={(e) => setFormData((prev) => ({ ...prev, report_type: e.target.value }))}
                >
                  {reportTypes.map((type) => (
                    <option key={type.value} value={type.value}>{type.label}</option>
                  ))}
                </select>
              </label>
              <label className="text-sm text-gray-700 dark:text-gray-300">
                Start Date
                <input
                  type="date"
                  className="mt-1 w-full rounded-md border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 px-3 py-2 text-sm"
                  value={formData.time_period_start}
                  onChange={(e) => setFormData((prev) => ({ ...prev, time_period_start: e.target.value }))}
                />
              </label>
              <label className="text-sm text-gray-700 dark:text-gray-300">
                End Date
                <input
                  type="date"
                  className="mt-1 w-full rounded-md border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 px-3 py-2 text-sm"
                  value={formData.time_period_end}
                  onChange={(e) => setFormData((prev) => ({ ...prev, time_period_end: e.target.value }))}
                />
              </label>
            </div>
            <div>
              <p className="text-sm text-gray-700 dark:text-gray-300 mb-2">Regions</p>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                {regions.length > 0 ? (
                  regions.map((region) => (
                    <label key={region.id} className="flex items-center gap-2 text-sm text-gray-700 dark:text-gray-300">
                      <input
                        type="checkbox"
                        checked={formData.regions.includes(region.id)}
                        onChange={() => toggleRegion(region.id)}
                      />
                      {region.name}
                    </label>
                  ))
                ) : (
                  <p className="text-sm text-gray-500">No regions available.</p>
                )}
              </div>
            </div>
            <div className="flex gap-2">
              <Button onClick={handleCreate} disabled={createReport.isLoading}>
                {createReport.isLoading ? 'Generating...' : 'Generate'}
              </Button>
              <Button variant="outline" onClick={() => setShowForm(false)}>Cancel</Button>
            </div>
          </CardContent>
        </Card>
      )}

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
                      <TableCell>{report.report_type || 'General'}</TableCell>
                      <TableCell>{report.created_at ? new Date(report.created_at).toLocaleString() : '-'}</TableCell>
                      <TableCell className="text-right">
                        <Button variant="outline" size="sm" onClick={() => handleDownload(report.id)}>
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
              <Button className="mt-4" onClick={() => setShowForm(true)}>
                <Plus className="h-4 w-4 mr-2"/>Generate Report
              </Button>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default Reports;
