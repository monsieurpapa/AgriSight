import React, { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '../components/ui/card';
import { Button } from '../components/ui/button';
import {
  LineChart,
  Line,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer
} from 'recharts';

// A minimal, read-only preview of the platform for unauthenticated users.
// Keep this light and stateless; no API calls.
const PublicDemo = () => {
  const [ndviData, setNdviData] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    const load = async () => {
      try {
        const resp = await fetch('/demo/ndvi.json', { cache: 'no-cache' });
        const json = await resp.json();
        setNdviData(json);
      } catch (e) {
        setError('Failed to load demo data');
      }
    };
    load();
  }, []);

  const ticks = useMemo(() => ndviData.map(d => d.date), [ndviData]);

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="mx-auto max-w-6xl px-4 py-10 sm:px-6 lg:px-8">
        <div className="mb-8 flex items-center justify-between">
          <h1 className="text-2xl font-semibold">AgriSight Demo</h1>
          <div className="flex gap-2">
            <Link to="/login"><Button variant="outline">Log in</Button></Link>
            <Link to="/register"><Button>Get started</Button></Link>
          </div>
        </div>

        <div className="grid gap-6 lg:grid-cols-2">
          <Card>
            <CardHeader>
              <CardTitle>Vegetation indices snapshot</CardTitle>
              <CardDescription>Sample NDVI chart and recent period trend.</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-56 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={ndviData} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                    <XAxis dataKey="date" ticks={ticks} tick={{ fontSize: 11 }} tickMargin={8} />
                    <YAxis domain={[0, 1]} tick={{ fontSize: 11 }} tickMargin={8} />
                    <Tooltip formatter={(v) => [Number(v).toFixed(2), 'NDVI']} labelFormatter={(l) => `Date: ${l}`} />
                    <Line type="monotone" dataKey="ndvi" stroke="#16a34a" strokeWidth={2} dot={{ r: 2 }} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
              <p className="mt-3 text-sm text-gray-600 dark:text-gray-300">Illustrative only. Sign in to explore real-time charts.</p>
              {error && <p className="mt-2 text-sm text-red-600">{error}</p>}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Map preview</CardTitle>
              <CardDescription>Example AOIs and overlays.</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="aspect-[16/10] w-full overflow-hidden rounded-lg border bg-white dark:border-gray-800 dark:bg-gray-900">
                <img src="/demo/map-preview.svg" alt="Map preview" className="h-full w-full object-cover" />
              </div>
              <p className="mt-3 text-sm text-gray-600 dark:text-gray-300">Interactive features require an account.</p>
            </CardContent>
          </Card>
        </div>

        <Card className="mt-6">
          <CardHeader>
            <CardTitle>What’s included in the full platform</CardTitle>
            <CardDescription>Alerts, exports, role-based access, and more.</CardDescription>
          </CardHeader>
          <CardContent>
            <ul className="list-inside list-disc text-sm text-gray-700 dark:text-gray-300">
              <li>NDVI, EVI, NDWI, SAVI with historical trends</li>
              <li>Stress events and anomaly detection</li>
              <li>Region management and team collaboration</li>
              <li>Downloadable reports and data exports</li>
            </ul>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default PublicDemo;


