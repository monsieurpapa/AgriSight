import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  MapPin,
  Satellite,
  AlertTriangle,
  TrendingUp,
  TrendingDown,
  Activity,
  Users,
  FileText,
  Eye,
  Download,
  Plus
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Alert, AlertDescription } from '../components/ui/alert';
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
import { useAuth } from '../contexts/AuthContext';
import { useWebSocketContext } from '../contexts/WebSocketContext';
import { dashboardAPI, satelliteProcessingAPI } from '../lib/api';
import APIError from '../components/error/APIError';
import { 
  formatDate, 
  formatRelativeTime, 
  getVegetationIndexColor,
  getVegetationIndexLabel,
  formatVegetationIndex,
  getRiskLevelColor,
  formatNumber,
  formatArea
} from '../lib/utils';

// Several endpoints backed by GeoDjango models (regions, stress events, conflict
// events) are served by a GeoFeatureModelSerializer, so their list data comes
// back as a GeoJSON FeatureCollection ({type, features: [...]}) rather than a
// plain array, with each item's fields nested under `.properties`. Normalize
// to flat objects so callers can use region.name / event.severity etc. as if
// it were a regular DRF list response.
export const toFlatFeatureList = (value) => {
  if (!value) return [];
  const features = Array.isArray(value) ? value : (value.features || []);
  return features.map(feature =>
    feature && feature.type === 'Feature'
      ? { id: feature.id, ...feature.properties, geometry: feature.geometry }
      : feature
  );
};

const Dashboard = () => {
  const { user, hasPermission } = useAuth();
  const { isConnected, realTimeData, notifications } = useWebSocketContext();
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [warnings, setWarnings] = useState([]);
  const navigate = useNavigate();

  // Fetch real dashboard data from APIs
  useEffect(() => {
    const fetchDashboardData = async (isRefresh = false) => {
      try {
        if (!isRefresh) {
          setLoading(true);
        }
        setError(null);
        
        // Fetch comprehensive dashboard data
        const data = await dashboardAPI.getDashboardData({
          includeOrganizations: hasPermission('manage_organizations'),
        });
        
        setWarnings(data.errors || []);

        const regionsData = data.regions || { count: 0, results: [] };
        const regionsList = toFlatFeatureList(regionsData.results);
        const regionsCount = regionsData.count ?? regionsList.length;
        const recentStressEvents = toFlatFeatureList(data.stressSummary?.recent_events);
        const recentConflictEvents = toFlatFeatureList(data.conflictSummary?.recent_events);
        const alertsData = data.alerts || { count: 0, results: [] };
        const reportsData = data.reports || { count: 0, results: [] };
        const organizationsData = data.organizations || { count: 0, results: [] };

        // Transform the data to match the expected format
        const transformedData = {
          stats: {
            totalRegions: regionsCount,
            activeRegions: regionsList.filter(r => r.is_active).length || 0,
            totalArea: regionsList.reduce((sum, r) => sum + (r.area_hectares || 0), 0) / 100 || 0, // Convert to km²
            lastUpdate: data.lastUpdate,
            processingTasks: data.processingStats?.active_tasks || 0,
            alertsCount: alertsData.count || 0,
            reportsGenerated: reportsData.count || 0,
            organizationsCount: organizationsData.count || 0
          },
          recentActivity: [
            // Recent stress events
            ...recentStressEvents.slice(0, 2).map(event => ({
              id: `stress-${event.id}`,
              type: 'alert',
              title: 'Agricultural stress detected',
              description: `${event.stress_type} stress in ${event.region?.name || 'Unknown region'}`,
              timestamp: event.detection_date,
              status: event.severity === 'high' ? 'warning' : 'completed'
            })),
            // Recent conflict events
            ...recentConflictEvents.slice(0, 1).map(event => ({
              id: `conflict-${event.id}`,
              type: 'alert',
              title: 'Conflict event reported',
              description: `${event.event_type} in ${event.region?.name || 'Unknown region'}`,
              timestamp: event.event_date,
              status: 'warning'
            })),
            // Processing activity
            {
              id: 'processing-1',
              type: 'processing',
              title: 'Satellite data processing',
              description: `${data.processingStats?.total_images_processed || 0} images processed`,
              timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
              status: 'completed'
            }
          ],
          vegetationTrends: [], // Will be populated by vegetation data API
          regionStatus: [
            { name: 'Healthy', value: data.stressSummary?.events_by_severity?.low || 0, color: '#10b981' },
            { name: 'Moderate', value: data.stressSummary?.events_by_severity?.medium || 0, color: '#f59e0b' },
            { name: 'Stressed', value: data.stressSummary?.events_by_severity?.high || 0, color: '#ef4444' },
            { name: 'No Data', value: Math.max(0, regionsCount - (data.stressSummary?.total_events || 0)), color: '#6b7280' }
          ],
          topRegions: regionsList.slice(0, 5).map(region => ({
            name: region.name,
            ndvi: 0.5, // Will be updated with real vegetation data
            area: region.area_hectares / 100, // Convert to km²
            status: 'healthy', // Will be determined by stress events
            change: 0 // Will be calculated from trend data
          })) || []
        };

        // Fetch vegetation trend data for the first few regions
        if (regionsList.length > 0) {
          try {
            const vegetationPromises = regionsList.slice(0, 3).map(region => 
              satelliteProcessingAPI.getRegionVegetationData(region.id, { days: 30 })
            );
            const vegetationData = await Promise.all(vegetationPromises);
            
            // Process vegetation data into trend format
            const trendData = {};
            vegetationData.forEach((regionData, index) => {
              if (regionData && regionData.length > 0) {
                regionData.forEach(point => {
                  const date = point.date;
                  if (!trendData[date]) {
                    trendData[date] = { date, ndvi: 0, evi: 0, ndwi: 0, savi: 0, count: 0 };
                  }
                  if (point.index_type === 'NDVI') trendData[date].ndvi += point.mean_value;
                  if (point.index_type === 'EVI') trendData[date].evi += point.mean_value;
                  if (point.index_type === 'NDWI') trendData[date].ndwi += point.mean_value;
                  if (point.index_type === 'SAVI') trendData[date].savi += point.mean_value;
                  trendData[date].count += 1;
                });
              }
            });
            
            // Average the values and convert to array
            transformedData.vegetationTrends = Object.values(trendData)
              .map(point => ({
                date: point.date,
                ndvi: point.count > 0 ? point.ndvi / point.count : 0,
                evi: point.count > 0 ? point.evi / point.count : 0,
                ndwi: point.count > 0 ? point.ndwi / point.count : 0,
                savi: point.count > 0 ? point.savi / point.count : 0
              }))
              .sort((a, b) => new Date(a.date) - new Date(b.date));
          } catch (vegetationError) {
            console.warn('Failed to fetch vegetation data:', vegetationError);
            setWarnings(prev => (prev || []).concat([{ error: vegetationError }]));
          }
        }

        setDashboardData(transformedData);
      } catch (err) {
        console.error('Failed to fetch dashboard data:', err);
        setError('Failed to load dashboard data. Please try again.');
      } finally {
        if (!isRefresh) {
          setLoading(false);
        }
      }
    };
    fetchDashboardData(false);
    const intervalId = setInterval(() => fetchDashboardData(true), 60000);
    return () => clearInterval(intervalId);
  }, [hasPermission]);

  // Handle real-time updates
  useEffect(() => {
    if (realTimeData && dashboardData) {
      // Update recent activity with new stress events
      const newStressEvents = realTimeData.stressEvents.slice(0, 2).map(event => ({
        id: `stress-${event.id}`,
        type: 'alert',
        title: 'Agricultural stress detected',
        description: `${event.stress_type} stress in ${event.region?.name || 'Unknown region'}`,
        timestamp: event.detection_date,
        status: event.severity === 'high' ? 'warning' : 'completed'
      }));

      // Update recent activity with new conflict events
      const newConflictEvents = (realTimeData.conflictEvents || []).slice(0, 1).map(event => ({
        id: `conflict-${event.id}`,
        type: 'alert',
        title: 'Conflict event reported',
        description: `${event.event_type} in ${event.region?.name || 'Unknown region'}`,
        timestamp: event.event_date,
        status: 'warning'
      }));

      // Update dashboard data with real-time information
      setDashboardData(prev => ({
        ...prev,
        stats: {
          ...prev.stats,
          alertsCount: (prev.stats.alertsCount || 0) + newStressEvents.length + newConflictEvents.length,
          processingTasks: realTimeData.processingTasks.filter(task => task.status === 'running').length
        },
        recentActivity: [
          ...newStressEvents,
          ...newConflictEvents,
          ...prev.recentActivity.slice(0, 3 - newStressEvents.length - newConflictEvents.length)
        ]
      }));
    }
  }, [realTimeData, dashboardData]);

  if (loading) {
    return (
      <div className="space-y-6">
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
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Welcome back, {user?.first_name}!
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">
            Here's what's happening with your agricultural monitoring system.
          </p>
        </div>
        
        <APIError 
          error={error}
          onRetry={() => window.location.reload()}
          title="Dashboard Loading Error"
          description="Failed to load dashboard data. Please try again."
        />
      </div>
    );
  }

  const { stats, recentActivity, vegetationTrends, regionStatus, topRegions } = dashboardData;
  const regionStatusTotal = regionStatus.reduce((sum, status) => sum + status.value, 0);

  return (
    <div className="space-y-6">
      {/* Welcome Section */}
      <div className="mb-8">
        {warnings.length > 0 && (
          <Alert className="mb-4">
            <AlertDescription>
              Some dashboard data could not be loaded. The view below may be incomplete.
            </AlertDescription>
          </Alert>
        )}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
              Welcome back, {user?.first_name}!
            </h1>
            <p className="text-gray-600 dark:text-gray-400 mt-2">
              Here's what's happening with your agricultural monitoring system.
            </p>
          </div>
          <div className="flex items-center space-x-4">
            {/* Real-time Status */}
            <div className="flex items-center space-x-2">
              <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
              <span className="text-sm text-gray-600 dark:text-gray-400">
                {isConnected ? 'Real-time connected' : 'Offline'}
              </span>
            </div>
            
            {/* Notifications Badge */}
            {notifications && notifications.length > 0 && (
              <div className="relative">
                <Button 
                  variant="outline" 
                  size="sm"
                  onClick={() => navigate('/alerts')}
                  className="relative"
                >
                  <AlertTriangle className="h-4 w-4 mr-2" />
                  Notifications
                  {notifications.filter(n => !n.read).length > 0 && (
                    <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">
                      {notifications.filter(n => !n.read).length}
                    </span>
                  )}
                </Button>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                  Total Regions
                </p>
                <p className="text-3xl font-bold text-gray-900 dark:text-white">
                  {stats.totalRegions}
                </p>
                <p className="text-sm text-green-600 dark:text-green-400 mt-1">
                  {stats.activeRegions} active
                </p>
              </div>
              <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900/20 rounded-lg flex items-center justify-center">
                <MapPin className="h-6 w-6 text-blue-600 dark:text-blue-400" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                  Total Area
                </p>
                <p className="text-3xl font-bold text-gray-900 dark:text-white">
                  {formatArea(stats.totalArea)}
                </p>
                <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                  Under monitoring
                </p>
              </div>
              <div className="w-12 h-12 bg-green-100 dark:bg-green-900/20 rounded-lg flex items-center justify-center">
                <Satellite className="h-6 w-6 text-green-600 dark:text-green-400" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                  Active Alerts
                </p>
                <p className="text-3xl font-bold text-gray-900 dark:text-white">
                  {stats.alertsCount}
                </p>
                <p className="text-sm text-red-600 dark:text-red-400 mt-1">
                  Requires attention
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
                  Processing Tasks
                </p>
                <p className="text-3xl font-bold text-gray-900 dark:text-white">
                  {stats.processingTasks}
                </p>
                <p className="text-sm text-yellow-600 dark:text-yellow-400 mt-1">
                  In progress
                </p>
              </div>
              <div className="w-12 h-12 bg-yellow-100 dark:bg-yellow-900/20 rounded-lg flex items-center justify-center">
                <Activity className="h-6 w-6 text-yellow-600 dark:text-yellow-400" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Vegetation Trends */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>Vegetation Index Trends</CardTitle>
                <CardDescription>
                  Weekly vegetation health indicators across all regions
                </CardDescription>
              </div>
              <div className="flex space-x-2">
                <Button variant="outline" size="sm">
                  <Download className="h-4 w-4 mr-2" />
                  Export
                </Button>
                <Button variant="outline" size="sm">
                  <Eye className="h-4 w-4 mr-2" />
                  Full View
                </Button>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="h-80">
              {vegetationTrends.length === 0 ? (
                <div className="h-full flex items-center justify-center text-sm text-gray-500">
                  No vegetation trend data available yet.
                </div>
              ) : (
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={vegetationTrends}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                  <XAxis 
                    dataKey="date" 
                    tickFormatter={(value) => formatDate(value, 'MMM dd')}
                    stroke="#6b7280"
                    fontSize={12}
                  />
                  <YAxis 
                    domain={[0, 1]} 
                    stroke="#6b7280"
                    fontSize={12}
                    tickFormatter={(value) => value.toFixed(2)}
                  />
                  <Tooltip 
                    labelFormatter={(value) => formatDate(value)}
                    formatter={(value, name) => [formatVegetationIndex(value), name.toUpperCase()]}
                    contentStyle={{
                      backgroundColor: 'white',
                      border: '1px solid #e5e7eb',
                      borderRadius: '8px',
                      boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                    }}
                  />
                  <Line 
                    type="monotone" 
                    dataKey="ndvi" 
                    stroke="#10b981" 
                    strokeWidth={3}
                    name="NDVI"
                    dot={{ fill: '#10b981', strokeWidth: 2, r: 4 }}
                    activeDot={{ r: 6, stroke: '#10b981', strokeWidth: 2 }}
                  />
                  <Line 
                    type="monotone" 
                    dataKey="evi" 
                    stroke="#3b82f6" 
                    strokeWidth={3}
                    name="EVI"
                    dot={{ fill: '#3b82f6', strokeWidth: 2, r: 4 }}
                    activeDot={{ r: 6, stroke: '#3b82f6', strokeWidth: 2 }}
                  />
                  <Line 
                    type="monotone" 
                    dataKey="ndwi" 
                    stroke="#06b6d4" 
                    strokeWidth={3}
                    name="NDWI"
                    dot={{ fill: '#06b6d4', strokeWidth: 2, r: 4 }}
                    activeDot={{ r: 6, stroke: '#06b6d4', strokeWidth: 2 }}
                  />
                  <Line 
                    type="monotone" 
                    dataKey="savi" 
                    stroke="#f59e0b" 
                    strokeWidth={3}
                    name="SAVI"
                    dot={{ fill: '#f59e0b', strokeWidth: 2, r: 4 }}
                    activeDot={{ r: 6, stroke: '#f59e0b', strokeWidth: 2 }}
                  />
                  </LineChart>
                </ResponsiveContainer>
              )}
            </div>
            <div className="mt-4 flex flex-wrap justify-center gap-4">
              {[
                { name: 'NDVI', color: '#10b981', description: 'Normalized Difference Vegetation Index' },
                { name: 'EVI', color: '#3b82f6', description: 'Enhanced Vegetation Index' },
                { name: 'NDWI', color: '#06b6d4', description: 'Normalized Difference Water Index' },
                { name: 'SAVI', color: '#f59e0b', description: 'Soil Adjusted Vegetation Index' }
              ].map((index) => (
                <div key={index.name} className="flex items-center space-x-2">
                  <div 
                    className="w-3 h-3 rounded-full"
                    style={{ backgroundColor: index.color }}
                  />
                  <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                    {index.name}
                  </span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Region Status Distribution */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>Region Health Status</CardTitle>
                <CardDescription>
                  Distribution of agricultural health across monitored regions
                </CardDescription>
              </div>
              <div className="flex space-x-2">
                <Button variant="outline" size="sm">
                  <Eye className="h-4 w-4 mr-2" />
                  Details
                </Button>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="h-80">
              {regionStatusTotal === 0 ? (
                <div className="h-full flex items-center justify-center text-sm text-gray-500">
                  No region health data available yet.
                </div>
              ) : (
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={regionStatus}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={120}
                      paddingAngle={5}
                      dataKey="value"
                      stroke="#fff"
                      strokeWidth={2}
                    >
                      {regionStatus.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip 
                      formatter={(value, name) => [value, name]}
                      contentStyle={{
                        backgroundColor: 'white',
                        border: '1px solid #e5e7eb',
                        borderRadius: '8px',
                        boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                      }}
                    />
                  </PieChart>
                </ResponsiveContainer>
              )}
            </div>
            <div className="grid grid-cols-2 gap-4 mt-4">
              {regionStatus.map((status, index) => (
                <div key={index} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <div 
                      className="w-4 h-4 rounded-full"
                      style={{ backgroundColor: status.color }}
                    />
                    <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                      {status.name}
                    </span>
                  </div>
                  <div className="text-right">
                    <div className="text-lg font-bold text-gray-900 dark:text-white">
                      {status.value}
                    </div>
                    <div className="text-xs text-gray-500 dark:text-gray-400">
                      {regionStatusTotal > 0 ? ((status.value / regionStatusTotal) * 100).toFixed(1) : '0.0'}%
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Bottom Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top Regions */}
        <Card>
          <CardHeader>
            <CardTitle>Region Performance</CardTitle>
            <CardDescription>
              Top regions by vegetation health and recent changes
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {topRegions.length === 0 ? (
                <div className="text-sm text-gray-500">
                  No region performance data available yet.
                </div>
              ) : (
                topRegions.map((region, index) => (
                  <div key={index} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                    <div className="flex-1">
                      <div className="flex items-center justify-between mb-1">
                        <h4 className="font-medium text-gray-900 dark:text-white">
                          {region.name}
                        </h4>
                        <Badge 
                          variant="outline"
                          className={getVegetationIndexColor(region.ndvi, 'NDVI')}
                        >
                          {getVegetationIndexLabel(region.ndvi, 'NDVI')}
                        </Badge>
                      </div>
                      <div className="flex items-center justify-between text-sm text-gray-600 dark:text-gray-400">
                        <span>NDVI: {formatVegetationIndex(region.ndvi)}</span>
                        <span>{formatArea(region.area)}</span>
                        <div className="flex items-center">
                          {region.change > 0 ? (
                            <TrendingUp className="h-4 w-4 text-green-500 mr-1" />
                          ) : (
                            <TrendingDown className="h-4 w-4 text-red-500 mr-1" />
                          )}
                          <span className={region.change > 0 ? 'text-green-600' : 'text-red-600'}>
                            {region.change > 0 ? '+' : ''}{formatVegetationIndex(region.change)}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          </CardContent>
        </Card>

        {/* Recent Activity */}
        <Card>
          <CardHeader>
            <CardTitle>Recent Activity</CardTitle>
            <CardDescription>
              Latest system activities and updates
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {recentActivity.length === 0 ? (
                <div className="text-sm text-gray-500">
                  No recent activity yet. Processing updates and alerts will appear here.
                </div>
              ) : (
                recentActivity.map((activity) => (
                  <div key={activity.id} className="flex items-start space-x-3">
                    <div className={`w-2 h-2 rounded-full mt-2 ${
                      activity.status === 'completed' ? 'bg-green-500' :
                      activity.status === 'warning' ? 'bg-yellow-500' :
                      activity.status === 'success' ? 'bg-blue-500' : 'bg-gray-500'
                    }`} />
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-900 dark:text-white">
                        {activity.title}
                      </p>
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        {activity.description}
                      </p>
                      <p className="text-xs text-gray-500 dark:text-gray-500 mt-1">
                        {formatRelativeTime(activity.timestamp)}
                      </p>
                    </div>
                  </div>
                ))
              )}
            </div>
            <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
              <Button variant="outline" size="sm" className="w-full">
                <Eye className="h-4 w-4 mr-2" />
                View All Activity
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Quick Actions</CardTitle>
          <CardDescription>
            Common tasks and shortcuts to help you get things done faster
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4">
            {hasPermission('view_data') && (
              <Button 
                variant="outline" 
                className="flex flex-col items-center p-4 h-auto hover:bg-green-50 hover:border-green-200 transition-colors"
                onClick={() => navigate('/satellite')}
              >
                <Satellite className="h-6 w-6 mb-2 text-green-600" />
                <span className="text-sm font-medium">Process Data</span>
                <span className="text-xs text-gray-500 mt-1">Satellite Analysis</span>
              </Button>
            )}
            {hasPermission('generate_reports') && (
              <Button 
                variant="outline" 
                className="flex flex-col items-center p-4 h-auto hover:bg-blue-50 hover:border-blue-200 transition-colors"
                onClick={() => navigate('/reports')}
              >
                <FileText className="h-6 w-6 mb-2 text-blue-600" />
                <span className="text-sm font-medium">Generate Report</span>
                <span className="text-xs text-gray-500 mt-1">Custom Reports</span>
              </Button>
            )}
            {hasPermission('manage_regions') && (
              <Button 
                variant="outline" 
                className="flex flex-col items-center p-4 h-auto hover:bg-purple-50 hover:border-purple-200 transition-colors"
                onClick={() => navigate('/regions')}
              >
                <Plus className="h-6 w-6 mb-2 text-purple-600" />
                <span className="text-sm font-medium">Add Region</span>
                <span className="text-xs text-gray-500 mt-1">New Monitoring</span>
              </Button>
            )}
            {hasPermission('view_data') && (
              <Button 
                variant="outline" 
                className="flex flex-col items-center p-4 h-auto hover:bg-red-50 hover:border-red-200 transition-colors"
                onClick={() => navigate('/alerts')}
              >
                <AlertTriangle className="h-6 w-6 mb-2 text-red-600" />
                <span className="text-sm font-medium">View Alerts</span>
                <span className="text-xs text-gray-500 mt-1">{stats.alertsCount} Active</span>
              </Button>
            )}
            {hasPermission('export_data') && (
              <Button 
                variant="outline" 
                className="flex flex-col items-center p-4 h-auto hover:bg-orange-50 hover:border-orange-200 transition-colors"
                onClick={() => navigate('/exports')}
              >
                <Download className="h-6 w-6 mb-2 text-orange-600" />
                <span className="text-sm font-medium">Export Data</span>
                <span className="text-xs text-gray-500 mt-1">Download Files</span>
              </Button>
            )}
            {hasPermission('manage_organizations') && (
              <Button 
                variant="outline" 
                className="flex flex-col items-center p-4 h-auto hover:bg-gray-50 hover:border-gray-200 transition-colors"
                onClick={() => navigate('/organizations')}
              >
                <Users className="h-6 w-6 mb-2 text-gray-600" />
                <span className="text-sm font-medium">Manage Users</span>
                <span className="text-xs text-gray-500 mt-1">User Admin</span>
              </Button>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default Dashboard;
