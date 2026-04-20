import React, { useState, useEffect, useRef } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { conflictReportsAPI, geospatialAPI } from '../lib/api';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { FileText, Download, RefreshCcw, AlertTriangle } from 'lucide-react';

const PHASE_COLORS = {
  'Phase 1': 'bg-green-100 text-green-800',
  'Phase 2': 'bg-yellow-100 text-yellow-800',
  'Phase 3': 'bg-orange-100 text-orange-800',
  'Phase 4': 'bg-red-100 text-red-800',
  'Phase 5': 'bg-red-700 text-white',
  'data_unavailable': 'bg-gray-100 text-gray-500 italic',
};

function phaseClass(phase) {
  for (const key of Object.keys(PHASE_COLORS)) {
    if (phase && phase.startsWith(key)) return PHASE_COLORS[key];
  }
  return PHASE_COLORS['data_unavailable'];
}

function formatDate(d) {
  return d ? new Date(d).toLocaleDateString() : '—';
}

export default function ReportGenerator() {
  const [selectedDistricts, setSelectedDistricts] = useState([]);
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [email, setEmail] = useState('');
  const [formError, setFormError] = useState('');
  const [activeReportId, setActiveReportId] = useState(null);
  const [pollActive, setPollActive] = useState(false);
  const [reportStatus, setReportStatus] = useState(null);
  const pollRef = useRef(null);

  const { data: regionsData } = useQuery({
    queryKey: ['conflict-districts'],
    queryFn: () => geospatialAPI.getRegions(),
  });

  const { data: reportsHistory, refetch: refetchHistory } = useQuery({
    queryKey: ['conflict-reports-list'],
    queryFn: () => conflictReportsAPI.list(),
  });

  const districts = (regionsData?.results || []).filter(
    (r) => ['North Kivu', 'Sud-Kivu', 'Ituri'].includes(r.province)
  );

  const generate = useMutation({
    mutationFn: (payload) => conflictReportsAPI.generate(payload),
    onSuccess: (data) => {
      setActiveReportId(data.id);
      setReportStatus({ status: 'PENDING' });
      setPollActive(true);
      refetchHistory();
    },
    onError: (err) => {
      const detail = err?.response?.data;
      setFormError(
        typeof detail === 'object'
          ? Object.values(detail).flat().join(' ')
          : 'Failed to generate report.'
      );
    },
  });

  // Poll report status every 3 seconds while processing
  useEffect(() => {
    if (!pollActive || !activeReportId) return;
    pollRef.current = setInterval(async () => {
      try {
        const status = await conflictReportsAPI.getStatus(activeReportId);
        setReportStatus(status);
        if (status.status === 'COMPLETE' || status.status === 'FAILED') {
          setPollActive(false);
          clearInterval(pollRef.current);
          refetchHistory();
        }
      } catch {
        setPollActive(false);
        clearInterval(pollRef.current);
      }
    }, 3000);
    return () => clearInterval(pollRef.current);
  }, [pollActive, activeReportId]);

  function toggleDistrict(id) {
    setSelectedDistricts((prev) =>
      prev.includes(id) ? prev.filter((d) => d !== id) : [...prev, id]
    );
  }

  function handleSubmit(e) {
    e.preventDefault();
    setFormError('');

    if (!selectedDistricts.length) {
      setFormError('Select at least one district.');
      return;
    }
    if (!startDate || !endDate) {
      setFormError('Both start and end date are required.');
      return;
    }
    const days = (new Date(endDate) - new Date(startDate)) / 86400000;
    if (days > 90) {
      setFormError('Date range cannot exceed 90 days.');
      return;
    }
    if (days <= 0) {
      setFormError('End date must be after start date.');
      return;
    }

    generate.mutate({
      district_ids: selectedDistricts,
      start_date: startDate,
      end_date: endDate,
      recipient_email: email,
    });
  }

  async function handleDownload(reportId) {
    try {
      const blob = await conflictReportsAPI.download(reportId);
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `agrisight_conflict_report_${reportId.slice(0, 8)}.pdf`;
      a.click();
      URL.revokeObjectURL(url);
    } catch {
      alert('Download failed. Report may not be ready yet.');
    }
  }

  const isProcessing = reportStatus?.status === 'PENDING' || reportStatus?.status === 'PROCESSING';
  const isComplete = reportStatus?.status === 'COMPLETE';
  const isFailed = reportStatus?.status === 'FAILED';

  const pastReports = reportsHistory?.results || reportsHistory || [];

  return (
    <div className="p-6 max-w-5xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Conflict-Aware Report Generator</h1>
        <p className="text-sm text-gray-500 mt-1">
          Eastern DRC — North Kivu, Sud-Kivu, Ituri. Generates IPC-aligned district risk summary PDF.
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Generate Report</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            {/* District selector */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Districts
              </label>
              {districts.length === 0 ? (
                <p className="text-sm text-gray-400 italic">
                  No DRC districts loaded. Run <code>load_ocha_boundaries</code> management command.
                </p>
              ) : (
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 max-h-48 overflow-y-auto border rounded p-2">
                  {districts.map((d) => (
                    <label key={d.id} className="flex items-center gap-2 text-sm cursor-pointer">
                      <input
                        type="checkbox"
                        checked={selectedDistricts.includes(d.id)}
                        onChange={() => toggleDistrict(d.id)}
                        className="rounded border-gray-300"
                      />
                      <span>{d.name}</span>
                      <span className="text-gray-400 text-xs">({d.province})</span>
                    </label>
                  ))}
                </div>
              )}
            </div>

            {/* Date range */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Start Date
                </label>
                <input
                  type="date"
                  value={startDate}
                  onChange={(e) => setStartDate(e.target.value)}
                  max={endDate || undefined}
                  className="w-full border rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500 dark:bg-gray-800 dark:border-gray-600 dark:text-white"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  End Date <span className="text-gray-400">(max 90 days)</span>
                </label>
                <input
                  type="date"
                  value={endDate}
                  onChange={(e) => setEndDate(e.target.value)}
                  min={startDate || undefined}
                  max={new Date().toISOString().split('T')[0]}
                  className="w-full border rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500 dark:bg-gray-800 dark:border-gray-600 dark:text-white"
                />
              </div>
            </div>

            {/* Email */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Email (optional — PDF will be attached)
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="analyst@org.org"
                className="w-full border rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500 dark:bg-gray-800 dark:border-gray-600 dark:text-white"
              />
            </div>

            {formError && (
              <div className="flex items-center gap-2 text-sm text-red-600 bg-red-50 border border-red-200 rounded px-3 py-2">
                <AlertTriangle className="h-4 w-4 flex-shrink-0" />
                {formError}
              </div>
            )}

            <Button
              type="submit"
              disabled={generate.isPending || isProcessing}
              className="w-full bg-green-700 hover:bg-green-800 text-white"
            >
              {generate.isPending || isProcessing ? (
                <><RefreshCcw className="h-4 w-4 mr-2 animate-spin" /> Generating...</>
              ) : (
                <><FileText className="h-4 w-4 mr-2" /> Generate Report</>
              )}
            </Button>
          </form>

          {/* Status feedback */}
          {reportStatus && (
            <div className={`mt-4 rounded px-4 py-3 text-sm ${
              isComplete ? 'bg-green-50 border border-green-200 text-green-800' :
              isFailed ? 'bg-red-50 border border-red-200 text-red-800' :
              'bg-blue-50 border border-blue-200 text-blue-800'
            }`}>
              {isProcessing && <><RefreshCcw className="inline h-3 w-3 mr-1 animate-spin" /> Processing report...</>}
              {isComplete && (
                <span>
                  Report ready.{' '}
                  <button
                    onClick={() => handleDownload(activeReportId)}
                    className="underline font-medium"
                  >
                    Download PDF
                  </button>
                  {reportStatus.email_status === 'SENT' && ' · Email sent.'}
                  {reportStatus.email_status === 'FAILED' && ' · Email delivery failed — download manually.'}
                </span>
              )}
              {isFailed && <span>Report generation failed. {reportStatus.error_message}</span>}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Recent reports */}
      {pastReports.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Recent Reports</CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b bg-gray-50 dark:bg-gray-800">
                  <th className="text-left px-4 py-2 font-medium text-gray-600">Period</th>
                  <th className="text-left px-4 py-2 font-medium text-gray-600">Status</th>
                  <th className="text-left px-4 py-2 font-medium text-gray-600">Created</th>
                  <th className="px-4 py-2"></th>
                </tr>
              </thead>
              <tbody>
                {pastReports.map((r) => (
                  <tr key={r.id} className="border-b last:border-0">
                    <td className="px-4 py-2">{formatDate(r.start_date)} – {formatDate(r.end_date)}</td>
                    <td className="px-4 py-2">
                      <span className={`px-2 py-0.5 rounded text-xs font-medium ${
                        r.status === 'COMPLETE' ? 'bg-green-100 text-green-700' :
                        r.status === 'FAILED' ? 'bg-red-100 text-red-700' :
                        'bg-blue-100 text-blue-700'
                      }`}>{r.status}</span>
                    </td>
                    <td className="px-4 py-2 text-gray-500">{formatDate(r.created_at)}</td>
                    <td className="px-4 py-2 text-right">
                      {r.status === 'COMPLETE' && (
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleDownload(r.id)}
                          className="text-xs"
                        >
                          <Download className="h-3 w-3 mr-1" /> PDF
                        </Button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
