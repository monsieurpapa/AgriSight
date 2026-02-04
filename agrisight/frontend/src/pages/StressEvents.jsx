import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Button } from '../components/ui/button';
import { AlertTriangle } from 'lucide-react';
import { analyticsAPI } from '../lib/api';
import { formatDate, formatRelativeTime } from '../lib/utils';

const StressEvents = () => {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const normalizeSeverityLevel = (severity) => {
    if (severity == null) return 'low';
    const numericSeverity = Number(severity);
    if (!Number.isNaN(numericSeverity)) {
      if (numericSeverity >= 4) return 'high';
      if (numericSeverity >= 2) return 'medium';
      return 'low';
    }
    const normalized = String(severity).toLowerCase();
    if (normalized === 'high' || normalized === 'medium' || normalized === 'low') {
      return normalized;
    }
    return 'low';
  };

  useEffect(() => {
    const fetchEvents = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await analyticsAPI.getStressEvents({ limit: 100 });
        const results = data?.results || data?.features || data || [];
        const normalized = results.map((event) => {
          const source = event?.properties ? event.properties : event;
          return {
            id: event?.id || source?.id,
            stress_type: source?.stress_type,
            region: source?.region_name || source?.region?.name || source?.region,
            detection_date: source?.detection_date,
            severity: normalizeSeverityLevel(source?.severity),
            description: source?.description
          };
        });
        setEvents(normalized);
      } catch (err) {
        console.error('Failed to fetch stress events:', err);
        setError('Failed to load stress events.');
      } finally {
        setLoading(false);
      }
    };

    fetchEvents();
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Stress Events</h1>
          <p className="text-gray-600 dark:text-gray-400">Latest agricultural stress detections</p>
        </div>
        <Button variant="outline" size="sm" onClick={() => window.location.reload()}>
          Refresh
        </Button>
      </div>
      <Card>
        <CardHeader>
          <CardTitle>Recent Events</CardTitle>
          <CardDescription>Detected anomalies</CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          {loading ? (
            <div className="py-12 text-center text-gray-600 dark:text-gray-400">Loading stress events...</div>
          ) : error ? (
            <div className="py-12 text-center text-red-600">{error}</div>
          ) : events.length > 0 ? (
            events.map((event) => (
              <div key={event.id} className="flex items-start gap-3 p-3 rounded-lg bg-gray-50 dark:bg-gray-800">
                <div className="w-8 h-8 rounded-full bg-red-100 dark:bg-red-900/20 flex items-center justify-center">
                  <AlertTriangle className="h-4 w-4 text-red-600"/>
                </div>
                <div className="flex-1">
                  <p className="font-medium text-gray-900 dark:text-white">
                    {event.stress_type ? `${event.stress_type} stress` : 'Stress Event'}
                  </p>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    {event.region || 'Unknown region'}
                  </p>
                  {event.detection_date && (
                    <p className="text-xs text-gray-500 mt-1">
                      {formatDate(event.detection_date)} ({formatRelativeTime(event.detection_date)})
                    </p>
                  )}
                </div>
                <Badge variant="outline">{event.severity}</Badge>
              </div>
            ))
          ) : (
            <div className="py-12 text-center text-gray-600 dark:text-gray-400">
              No stress events found
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default StressEvents;


