import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { 
  TrendingUp, 
  TrendingDown, 
  AlertTriangle, 
  Activity, 
  BarChart3, 
  PieChart as PieChartIcon,
  Calendar,
  Download,
  Filter
} from 'lucide-react';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell
} from 'recharts';
import { analyticsAPI, satelliteProcessingAPI, geospatialAPI } from '../lib/api';
import { formatDate, formatRelativeTime, formatVegetationIndex, getVegetationIndexColor } from '../lib/utils';

const Analytics = () => {
  const [stressSummary, setStressSummary] = useState(null);
  const [conflictSummary, setConflictSummary] = useState(null);
  const [trendData, setTrendData] = useState(null);
  const [regions, setRegions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedTimeRange, setSelectedTimeRange] = useState('30'); // days

  // Fetch analytics data
  useEffect(() => {
    const fetchAnalyticsData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        // Fetch all analytics data in parallel
        const [stressData, conflictData, regionsData, trendAnalysis] = await Promise.all([
          analyticsAPI.getStressEventSummary({ days: parseInt(selectedTimeRange) }),
          analyticsAPI.getConflictEventSummary({ days: parseInt(selectedTimeRange) }),
          geospatialAPI.getRegions(),
          satelliteProcessingAPI.getTrendAnalysis({ days: parseInt(selectedTimeRange) })
        ]);
        
        setStressSummary(stressData);
        setConflictSummary(conflictData);
        setRegions(regionsData.results || []);
        setTrendData(trendAnalysis);
      } catch (err) {
        console.error('Failed to fetch analytics data:', err);
        setError('Failed to load analytics data. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    fetchAnalyticsData();
  }, [selectedTimeRange]);

  // Process stress events by type for pie chart
  const stressEventsByType = stressSummary ? Object.entries(stressSummary.events_by_type || {}).map(([type, count]) => ({
    name: type.charAt(0).toUpperCase() + type.slice(1),
    value: count,
    color: type === 'drought' ? '#ef4444' : 
           type === 'flood' ? '#3b82f6' : 
           type === 'pest' ? '#f59e0b' : 
           type === 'disease' ? '#8b5cf6' : '#10b981'
  })) : [];

  // Process stress events by severity for bar chart
  const stressEventsBySeverity = stressSummary ? Object.entries(stressSummary.events_by_severity || {}).map(([severity, count]) => ({
    severity: severity.charAt(0).toUpperCase() + severity.slice(1),
    count: count,
    color: severity === 'high' ? '#ef4444' : 
           severity === 'medium' ? '#f59e0b' : '#10b981'
  })) : [];

  // Process conflict events by type
  const conflictEventsByType = conflictSummary ? Object.entries(conflictSummary.events_by_type || {}).map(([type, count]) => ({
    name: type.charAt(0).toUpperCase() + type.slice(1),
    value: count,
    color: type === 'armed_conflict' ? '#ef4444' : 
           type === 'civil_unrest' ? '#f59e0b' : 
           type === 'displacement' ? '#8b5cf6' : '#6b7280'
  })) : [];

  if (loading) {
    return (
      <div className="space-y-6">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Analytics</h1>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {[...Array(4)].map((_, i) => (
            <Card key={i}>
              <CardContent className="p-6">
                <div className="animate-pulse">
                  <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
                  <div className="h-8 bg-gray-200 rounded w-1/2"></div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-6">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Analytics</h1>
        <Card className="border-red-200 bg-red-50 dark:bg-red-900/10">
          <CardContent className="p-6">
            <div className="flex items-center space-x-3">
              <AlertTriangle className="h-6 w-6 text-red-600" />
              <div>
                <h3 className="text-lg font-semibold text-red-800 dark:text-red-200">
                  Error Loading Analytics
                </h3>
                <p className="text-red-600 dark:text-red-300 mt-1">
                  {error}
                </p>
                <Button 
                  variant="outline" 
                  size="sm" 
                  className="mt-3"
                  onClick={() => window.location.reload()}
                >
                  Retry
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Analytics</h1>
          <p className="text-gray-600 dark:text-gray-400">Agricultural monitoring insights and trends</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm">
            <Filter className="h-4 w-4 mr-2"/>
            Filter
          </Button>
          <Button variant="outline" size="sm">
            <Download className="h-4 w-4 mr-2"/>
            Export
          </Button>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                  Total Stress Events
                </p>
                <p className="text-3xl font-bold text-gray-900 dark:text-white">
                  {stressSummary?.total_events || 0}
                </p>
                <p className="text-sm text-red-600 dark:text-red-400 mt-1">
                  Last {selectedTimeRange} days
                </p>
              </div>
              <div className="w-12 h-12 bg-red-100 dark:bg-red-900/20 rounded-lg flex items-center justify-center">
                <AlertTriangle className="h-6 w-6 text-red-600 dark:text-red-400" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                  Total Conflict Events
                </p>
                <p className="text-3xl font-bold text-gray-900 dark:text-white">
                  {conflictSummary?.total_events || 0}
                </p>
                <p className="text-sm text-orange-600 dark:text-orange-400 mt-1">
                  Last {selectedTimeRange} days
                </p>
              </div>
              <div className="w-12 h-12 bg-orange-100 dark:bg-orange-900/20 rounded-lg flex items-center justify-center">
                <Activity className="h-6 w-6 text-orange-600 dark:text-orange-400" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                  Affected Area
                </p>
                <p className="text-3xl font-bold text-gray-900 dark:text-white">
                  {stressSummary?.total_affected_area ? (stressSummary.total_affected_area / 100).toFixed(1) : 0}
                </p>
                <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                  km²
                </p>
              </div>
              <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900/20 rounded-lg flex items-center justify-center">
                <BarChart3 className="h-6 w-6 text-blue-600 dark:text-blue-400" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                  Monitored Regions
                </p>
                <p className="text-3xl font-bold text-gray-900 dark:text-white">
                  {regions.length}
                </p>
                <p className="text-sm text-green-600 dark:text-green-400 mt-1">
                  Active monitoring
                </p>
              </div>
              <div className="w-12 h-12 bg-green-100 dark:bg-green-900/20 rounded-lg flex items-center justify-center">
                <TrendingUp className="h-6 w-6 text-green-600 dark:text-green-400" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Time Range Selector */}
      <Card>
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Time Range</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">Select the analysis period</p>
            </div>
            <div className="flex gap-2">
              {['7', '30', '90', '365'].map((days) => (
                <Button
                  key={days}
                  variant={selectedTimeRange === days ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setSelectedTimeRange(days)}
                >
                  {days === '365' ? '1 Year' : `${days} Days`}
                </Button>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Analytics Tabs */}
      <Tabs defaultValue="stress" className="space-y-6">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="stress">Stress Events</TabsTrigger>
          <TabsTrigger value="conflict">Conflict Events</TabsTrigger>
          <TabsTrigger value="trends">Trends</TabsTrigger>
        </TabsList>

        <TabsContent value="stress" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Stress Events by Type */}
            <Card>
              <CardHeader>
                <CardTitle>Stress Events by Type</CardTitle>
                <CardDescription>Distribution of agricultural stress events</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-80">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={stressEventsByType}
                        cx="50%"
                        cy="50%"
                        innerRadius={60}
                        outerRadius={120}
                        paddingAngle={5}
                        dataKey="value"
                      >
                        {stressEventsByType.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
                <div className="flex flex-wrap justify-center gap-4 mt-4">
                  {stressEventsByType.map((entry, index) => (
                    <div key={index} className="flex items-center space-x-2">
                      <div 
                        className="w-3 h-3 rounded-full"
                        style={{ backgroundColor: entry.color }}
                      />
                      <span className="text-sm text-gray-600 dark:text-gray-400">
                        {entry.name} ({entry.value})
                      </span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Stress Events by Severity */}
            <Card>
              <CardHeader>
                <CardTitle>Stress Events by Severity</CardTitle>
                <CardDescription>Severity distribution of stress events</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-80">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={stressEventsBySeverity}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="severity" />
                      <YAxis />
                      <Tooltip />
                      <Bar dataKey="count" fill="#8884d8" />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Recent Stress Events */}
          <Card>
            <CardHeader>
              <CardTitle>Recent Stress Events</CardTitle>
              <CardDescription>Latest agricultural stress detections</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {stressSummary?.recent_events?.slice(0, 5).map((event) => (
                  <div key={event.id} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                    <div className="flex items-center space-x-3">
                      <div className={`w-2 h-2 rounded-full ${
                        event.severity === 'high' ? 'bg-red-500' :
                        event.severity === 'medium' ? 'bg-yellow-500' : 'bg-green-500'
                      }`} />
                      <div>
                        <p className="font-medium text-gray-900 dark:text-white">
                          {event.stress_type} stress
                        </p>
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                          {event.region?.name || 'Unknown region'}
                        </p>
                      </div>
                    </div>
                    <div className="text-right">
                      <Badge variant="outline" className={
                        event.severity === 'high' ? 'border-red-500 text-red-600' :
                        event.severity === 'medium' ? 'border-yellow-500 text-yellow-600' : 
                        'border-green-500 text-green-600'
                      }>
                        {event.severity}
                      </Badge>
                      <p className="text-xs text-gray-500 mt-1">
                        {formatRelativeTime(event.detection_date)}
                      </p>
                    </div>
                  </div>
                )) || (
                  <p className="text-gray-500 dark:text-gray-400 text-center py-8">
                    No recent stress events found
                  </p>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="conflict" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Conflict Events by Type */}
            <Card>
              <CardHeader>
                <CardTitle>Conflict Events by Type</CardTitle>
                <CardDescription>Distribution of conflict events</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-80">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={conflictEventsByType}
                        cx="50%"
                        cy="50%"
                        innerRadius={60}
                        outerRadius={120}
                        paddingAngle={5}
                        dataKey="value"
                      >
                        {conflictEventsByType.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
                <div className="flex flex-wrap justify-center gap-4 mt-4">
                  {conflictEventsByType.map((entry, index) => (
                    <div key={index} className="flex items-center space-x-2">
                      <div 
                        className="w-3 h-3 rounded-full"
                        style={{ backgroundColor: entry.color }}
                      />
                      <span className="text-sm text-gray-600 dark:text-gray-400">
                        {entry.name} ({entry.value})
                      </span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Conflict Events by Intensity */}
            <Card>
              <CardHeader>
                <CardTitle>Conflict Events by Intensity</CardTitle>
                <CardDescription>Intensity distribution of conflict events</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-80">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={Object.entries(conflictSummary?.events_by_intensity || {}).map(([intensity, count]) => ({
                      intensity: intensity.charAt(0).toUpperCase() + intensity.slice(1),
                      count: count
                    }))}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="intensity" />
                      <YAxis />
                      <Tooltip />
                      <Bar dataKey="count" fill="#8884d8" />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Recent Conflict Events */}
          <Card>
            <CardHeader>
              <CardTitle>Recent Conflict Events</CardTitle>
              <CardDescription>Latest conflict event reports</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {conflictSummary?.recent_events?.slice(0, 5).map((event) => (
                  <div key={event.id} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                    <div className="flex items-center space-x-3">
                      <div className="w-2 h-2 rounded-full bg-red-500" />
                      <div>
                        <p className="font-medium text-gray-900 dark:text-white">
                          {event.event_type}
                        </p>
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                          {event.region?.name || 'Unknown region'}
                        </p>
                      </div>
                    </div>
                    <div className="text-right">
                      <Badge variant="outline" className="border-red-500 text-red-600">
                        {event.intensity}
                      </Badge>
                      <p className="text-xs text-gray-500 mt-1">
                        {formatRelativeTime(event.event_date)}
                      </p>
                    </div>
                  </div>
                )) || (
                  <p className="text-gray-500 dark:text-gray-400 text-center py-8">
                    No recent conflict events found
                  </p>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="trends" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Vegetation Trends</CardTitle>
              <CardDescription>Vegetation index trends over time</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-80">
                {trendData && trendData.length > 0 ? (
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={trendData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis 
                        dataKey="date" 
                        tickFormatter={(value) => formatDate(value, 'MMM dd')}
                      />
                      <YAxis domain={[0, 1]} />
                      <Tooltip 
                        labelFormatter={(value) => formatDate(value)}
                        formatter={(value, name) => [formatVegetationIndex(value), name.toUpperCase()]}
                      />
                      <Line 
                        type="monotone" 
                        dataKey="ndvi" 
                        stroke="#10b981" 
                        strokeWidth={2}
                        name="NDVI"
                      />
                      <Line 
                        type="monotone" 
                        dataKey="evi" 
                        stroke="#3b82f6" 
                        strokeWidth={2}
                        name="EVI"
                      />
                      <Line 
                        type="monotone" 
                        dataKey="ndwi" 
                        stroke="#06b6d4" 
                        strokeWidth={2}
                        name="NDWI"
                      />
                    </LineChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="flex items-center justify-center h-full text-gray-500">
                    <div className="text-center">
                      <TrendingUp className="h-8 w-8 mx-auto mb-2" />
                      <p>No trend data available</p>
                    </div>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default Analytics;


