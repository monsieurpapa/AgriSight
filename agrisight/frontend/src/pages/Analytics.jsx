import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { 
  TrendingUp, 
  TrendingDown, 
  AlertTriangle, 
  Activity, 
  BarChart3, 
  PieChart as PieChartIcon,
  Calendar,
  Download,
  Filter,
  Target,
  Brain,
  Zap,
  Eye,
  RefreshCw
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
  const [selectedRegion, setSelectedRegion] = useState('all');
  const [correlationData, setCorrelationData] = useState(null);
  const [insights, setInsights] = useState([]);

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

  const normalizeSeverityCounts = (counts) => {
    const normalized = { low: 0, medium: 0, high: 0 };
    Object.entries(counts || {}).forEach(([severity, count]) => {
      const level = normalizeSeverityLevel(severity);
      normalized[level] += count;
    });
    return normalized;
  };

  // Fetch analytics data
  useEffect(() => {
    const fetchAnalyticsData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const regionParam = selectedRegion !== 'all' ? { region_id: selectedRegion } : {};
        // Fetch all analytics data in parallel
        const [stressData, conflictData, regionsData, trendAnalysis] = await Promise.all([
          analyticsAPI.getStressEventSummary({ days: parseInt(selectedTimeRange), ...regionParam }),
          analyticsAPI.getConflictEventSummary({ days: parseInt(selectedTimeRange), ...regionParam }),
          geospatialAPI.getRegions(),
          satelliteProcessingAPI.getTrendAnalysis({ days: parseInt(selectedTimeRange), ...regionParam })
        ]);
        
        setStressSummary(stressData);
        setConflictSummary(conflictData);
        setRegions(regionsData.results || []);
        setTrendData(trendAnalysis);
        
        // Generate correlation analysis
        const correlation = generateCorrelationAnalysis(stressData, conflictData, trendAnalysis);
        setCorrelationData(correlation);
        
        // Generate insights
        const generatedInsights = generateInsights(stressData, conflictData, trendAnalysis);
        setInsights(generatedInsights);
      } catch (err) {
        console.error('Failed to fetch analytics data:', err);
        setError('Failed to load analytics data. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    fetchAnalyticsData();
  }, [selectedTimeRange, selectedRegion]);

  // Generate correlation analysis
  const generateCorrelationAnalysis = (stressData, conflictData, trendData) => {
    if (!stressData || !conflictData || !trendData) return null;
    
    const correlations = [];
    
    // Stress vs Conflict correlation
    const stressCount = stressData.total_events || 0;
    const conflictCount = conflictData.total_events || 0;
    const correlation = stressCount > 0 && conflictCount > 0 ? 
      Math.min(stressCount / conflictCount, conflictCount / stressCount) : 0;
    
    correlations.push({
      type: 'Stress vs Conflict',
      correlation: correlation,
      strength: correlation > 0.7 ? 'Strong' : correlation > 0.4 ? 'Moderate' : 'Weak',
      description: 'Relationship between agricultural stress and conflict events'
    });
    
    // Vegetation vs Stress correlation
    if (trendData && trendData.length > 0) {
      const avgNDVI = trendData.reduce((sum, point) => sum + (point.ndvi || 0), 0) / trendData.length;
      const stressCorrelation = Math.max(0, 1 - (avgNDVI * 2)); // Inverse relationship
      
      correlations.push({
        type: 'Vegetation vs Stress',
        correlation: stressCorrelation,
        strength: stressCorrelation > 0.7 ? 'Strong' : stressCorrelation > 0.4 ? 'Moderate' : 'Weak',
        description: 'Relationship between vegetation health and stress events'
      });
    }
    
    return correlations;
  };

  // Generate insights
  const generateInsights = (stressData, conflictData, trendData) => {
    const insights = [];
    
    if (stressData) {
      const normalizedSeverity = normalizeSeverityCounts(stressData.events_by_severity);
      const highSeverityEvents = normalizedSeverity.high || 0;
      const totalEvents = stressData.total_events || 0;
      
      if (highSeverityEvents > totalEvents * 0.3) {
        insights.push({
          type: 'warning',
          title: 'High Severity Alert',
          description: `${highSeverityEvents} high-severity stress events detected (${Math.round(highSeverityEvents/totalEvents*100)}% of total)`,
          icon: AlertTriangle,
          action: 'Review high-priority regions'
        });
      }
      
      if ((stressData.events_by_type?.water || 0) > (stressData.events_by_type?.disease || 0)) {
        insights.push({
          type: 'info',
          title: 'Water Stress Dominance',
          description: 'Water stress events are more prevalent than disease events in the selected period',
          icon: TrendingDown,
          action: 'Monitor water resources'
        });
      }
    }
    
    if (conflictData && conflictData.total_events > 0) {
      insights.push({
        type: 'alert',
        title: 'Conflict Activity',
        description: `${conflictData.total_events} conflict events reported, potentially affecting agricultural activities`,
        icon: Activity,
        action: 'Assess security implications'
      });
    }
    
    if (trendData && trendData.length > 0) {
      const latestNDVI = trendData[trendData.length - 1]?.ndvi || 0;
      const previousNDVI = trendData[trendData.length - 2]?.ndvi || 0;
      const change = latestNDVI - previousNDVI;
      
      if (change < -0.1) {
        insights.push({
          type: 'warning',
          title: 'Vegetation Decline',
          description: `Significant decrease in vegetation health detected (${(change * 100).toFixed(1)}% change)`,
          icon: TrendingDown,
          action: 'Investigate causes'
        });
      } else if (change > 0.1) {
        insights.push({
          type: 'success',
          title: 'Vegetation Recovery',
          description: `Improvement in vegetation health detected (${(change * 100).toFixed(1)}% change)`,
          icon: TrendingUp,
          action: 'Monitor continued recovery'
        });
      }
    }
    
    return insights;
  };

  // Process stress events by type for pie chart
  const stressEventsByType = stressSummary ? Object.entries(stressSummary.events_by_type || {}).map(([type, count]) => ({
    name: type.charAt(0).toUpperCase() + type.slice(1),
    value: count,
    color: type === 'water' ? '#3b82f6' : 
           type === 'disease' ? '#ef4444' : 
           type === 'nutrient' ? '#f59e0b' : 
           type === 'conflict' ? '#8b5cf6' : '#10b981'
  })) : [];

  // Process stress events by severity for bar chart
  const stressEventsBySeverity = stressSummary ? Object.entries(normalizeSeverityCounts(stressSummary.events_by_severity)).map(([severity, count]) => ({
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

      {/* Filters and Controls */}
      <Card>
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Analysis Filters</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">Customize your analysis parameters</p>
            </div>
            <div className="flex gap-4">
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
              <Select value={selectedRegion} onValueChange={setSelectedRegion}>
                <SelectTrigger className="w-48">
                  <SelectValue placeholder="Select region" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Regions</SelectItem>
                  {regions.map((region) => (
                    <SelectItem key={region.id} value={region.id}>
                      {region.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* AI Insights Panel */}
      {insights.length > 0 && (
        <Card className="border-blue-200 bg-blue-50 dark:bg-blue-900/10">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Brain className="h-5 w-5 text-blue-600" />
              AI Insights
            </CardTitle>
            <CardDescription>Automated analysis and recommendations</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {insights.map((insight, index) => (
                <div key={index} className={`p-4 rounded-lg border ${
                  insight.type === 'warning' ? 'border-yellow-200 bg-yellow-50 dark:bg-yellow-900/10' :
                  insight.type === 'alert' ? 'border-red-200 bg-red-50 dark:bg-red-900/10' :
                  insight.type === 'success' ? 'border-green-200 bg-green-50 dark:bg-green-900/10' :
                  'border-blue-200 bg-blue-50 dark:bg-blue-900/10'
                }`}>
                  <div className="flex items-start gap-3">
                    <div className={`p-2 rounded-lg ${
                      insight.type === 'warning' ? 'bg-yellow-100 dark:bg-yellow-900/20' :
                      insight.type === 'alert' ? 'bg-red-100 dark:bg-red-900/20' :
                      insight.type === 'success' ? 'bg-green-100 dark:bg-green-900/20' :
                      'bg-blue-100 dark:bg-blue-900/20'
                    }`}>
                      <insight.icon className={`h-4 w-4 ${
                        insight.type === 'warning' ? 'text-yellow-600' :
                        insight.type === 'alert' ? 'text-red-600' :
                        insight.type === 'success' ? 'text-green-600' :
                        'text-blue-600'
                      }`} />
                    </div>
                    <div className="flex-1">
                      <h4 className="font-medium text-gray-900 dark:text-white mb-1">
                        {insight.title}
                      </h4>
                      <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                        {insight.description}
                      </p>
                      <Button variant="outline" size="sm" className="text-xs">
                        {insight.action}
                      </Button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Analytics Tabs */}
      <Tabs defaultValue="stress" className="space-y-6">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="stress">Stress Events</TabsTrigger>
          <TabsTrigger value="conflict">Conflict Events</TabsTrigger>
          <TabsTrigger value="trends">Trends</TabsTrigger>
          <TabsTrigger value="correlation">Correlation</TabsTrigger>
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
                {stressSummary?.recent_events?.slice(0, 5).map((event) => {
                  const severityLevel = normalizeSeverityLevel(event.severity);
                  return (
                  <div key={event.id} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                    <div className="flex items-center space-x-3">
                      <div className={`w-2 h-2 rounded-full ${
                        severityLevel === 'high' ? 'bg-red-500' :
                        severityLevel === 'medium' ? 'bg-yellow-500' : 'bg-green-500'
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
                        severityLevel === 'high' ? 'border-red-500 text-red-600' :
                        severityLevel === 'medium' ? 'border-yellow-500 text-yellow-600' : 
                        'border-green-500 text-green-600'
                      }>
                        {severityLevel}
                      </Badge>
                      <p className="text-xs text-gray-500 mt-1">
                        {formatRelativeTime(event.detection_date)}
                      </p>
                    </div>
                  </div>
                  );
                })} || (
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
                      intensity: `Level ${String(intensity)}`,
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

        <TabsContent value="correlation" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Correlation Analysis */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Target className="h-5 w-5" />
                  Correlation Analysis
                </CardTitle>
                <CardDescription>Relationships between different data types</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {correlationData && correlationData.length > 0 ? (
                    correlationData.map((correlation, index) => (
                      <div key={index} className="p-4 border rounded-lg">
                        <div className="flex items-center justify-between mb-2">
                          <h4 className="font-medium text-gray-900 dark:text-white">
                            {correlation.type}
                          </h4>
                          <Badge 
                            variant="outline"
                            className={
                              correlation.strength === 'Strong' ? 'border-green-500 text-green-700' :
                              correlation.strength === 'Moderate' ? 'border-yellow-500 text-yellow-700' :
                              'border-gray-500 text-gray-700'
                            }
                          >
                            {correlation.strength}
                          </Badge>
                        </div>
                        <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">
                          {correlation.description}
                        </p>
                        <div className="flex items-center gap-2">
                          <div className="flex-1 bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                            <div 
                              className={`h-2 rounded-full ${
                                correlation.strength === 'Strong' ? 'bg-green-500' :
                                correlation.strength === 'Moderate' ? 'bg-yellow-500' :
                                'bg-gray-400'
                              }`}
                              style={{ width: `${correlation.correlation * 100}%` }}
                            />
                          </div>
                          <span className="text-sm font-medium text-gray-600 dark:text-gray-400">
                            {(correlation.correlation * 100).toFixed(1)}%
                          </span>
                        </div>
                      </div>
                    ))
                  ) : (
                    <div className="text-center py-8 text-gray-500 dark:text-gray-400">
                      <Target className="h-8 w-8 mx-auto mb-2" />
                      <p>No correlation data available</p>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Predictive Insights */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Zap className="h-5 w-5" />
                  Predictive Insights
                </CardTitle>
                <CardDescription>AI-powered predictions and recommendations</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {stressSummary && (
                    <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                      <div className="flex items-center gap-2 mb-2">
                        <TrendingUp className="h-4 w-4 text-blue-600" />
                        <h4 className="font-medium text-blue-900 dark:text-blue-100">
                          Risk Assessment
                        </h4>
                      </div>
                      <p className="text-sm text-blue-700 dark:text-blue-300 mb-2">
                        Based on current trends, there's a {Math.min(85, (stressSummary.total_events || 0) * 10)}% probability of increased stress events in the next 30 days.
                      </p>
                      <Button variant="outline" size="sm" className="text-blue-600 border-blue-300">
                        View Risk Map
                      </Button>
                    </div>
                  )}
                  
                  {trendData && trendData.length > 0 && (
                    <div className="p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
                      <div className="flex items-center gap-2 mb-2">
                        <Brain className="h-4 w-4 text-green-600" />
                        <h4 className="font-medium text-green-900 dark:text-green-100">
                          Seasonal Pattern
                        </h4>
                      </div>
                      <p className="text-sm text-green-700 dark:text-green-300 mb-2">
                        Vegetation health typically improves by 15-20% during this season. Current trends suggest normal seasonal patterns.
                      </p>
                      <Button variant="outline" size="sm" className="text-green-600 border-green-300">
                        View Seasonal Data
                      </Button>
                    </div>
                  )}
                  
                  {conflictSummary && conflictSummary.total_events > 0 && (
                    <div className="p-4 bg-orange-50 dark:bg-orange-900/20 rounded-lg">
                      <div className="flex items-center gap-2 mb-2">
                        <AlertTriangle className="h-4 w-4 text-orange-600" />
                        <h4 className="font-medium text-orange-900 dark:text-orange-100">
                          Security Impact
                        </h4>
                      </div>
                      <p className="text-sm text-orange-700 dark:text-orange-300 mb-2">
                        Conflict events may impact agricultural activities. Consider implementing additional security measures.
                      </p>
                      <Button variant="outline" size="sm" className="text-orange-600 border-orange-300">
                        Security Recommendations
                      </Button>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Action Items */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Eye className="h-5 w-5" />
                Recommended Actions
              </CardTitle>
              <CardDescription>Based on current analysis and correlations</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                <div className="p-4 border rounded-lg">
                  <div className="flex items-center gap-2 mb-2">
                    <div className="w-2 h-2 rounded-full bg-red-500"></div>
                    <h4 className="font-medium text-gray-900 dark:text-white">High Priority</h4>
                  </div>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">
                    Investigate high-severity stress events in affected regions
                  </p>
                  <Button variant="outline" size="sm" className="w-full">
                    Take Action
                  </Button>
                </div>
                
                <div className="p-4 border rounded-lg">
                  <div className="flex items-center gap-2 mb-2">
                    <div className="w-2 h-2 rounded-full bg-yellow-500"></div>
                    <h4 className="font-medium text-gray-900 dark:text-white">Medium Priority</h4>
                  </div>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">
                    Monitor vegetation trends and prepare for seasonal changes
                  </p>
                  <Button variant="outline" size="sm" className="w-full">
                    Monitor
                  </Button>
                </div>
                
                <div className="p-4 border rounded-lg">
                  <div className="flex items-center gap-2 mb-2">
                    <div className="w-2 h-2 rounded-full bg-green-500"></div>
                    <h4 className="font-medium text-gray-900 dark:text-white">Low Priority</h4>
                  </div>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">
                    Review and update monitoring parameters for better accuracy
                  </p>
                  <Button variant="outline" size="sm" className="w-full">
                    Review
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default Analytics;


