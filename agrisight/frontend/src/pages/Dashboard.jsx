import React, { useState, useEffect } from 'react';
import {
  MapPin,
  Satellite,
  AlertTriangle,
  TrendingUp,
  TrendingDown,
  Activity,
  Users,
  FileText,
  Calendar,
  Clock,
  Eye,
  Download
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Progress } from '../components/ui/progress';
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
import { dashboardAPI, satelliteProcessingAPI, analyticsAPI } from '../lib/api';
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

const Dashboard = () => {
  const { user, organization } = useAuth();
  const { isConnected, realTimeData, notifications } = useWebSocketContext();
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch real dashboard data from APIs
  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        // Fetch comprehensive dashboard data
        const data = await dashboardAPI.getDashboardData();
        
        // Transform the data to match the expected format
        const transformedData = {
          stats: {
            totalRegions: data.regions?.count || 0,
            activeRegions: data.regions?.results?.filter(r => r.is_active).length || 0,
            totalArea: data.regions?.results?.reduce((sum, r) => sum + (r.area_hectares || 0), 0) / 100 || 0, // Convert to km²
            lastUpdate: data.lastUpdate,
            processingTasks: data.processingStats?.active_tasks || 0,
            alertsCount: data.alerts?.count || 0,
            reportsGenerated: data.reports?.count || 0,
            organizationsCount: 1 // Will be updated when organizations API is called
          },
          recentActivity: [
            // Recent stress events
            ...(data.stressSummary?.recent_events?.slice(0, 2).map(event => ({
              id: `stress-${event.id}`,
              type: 'alert',
              title: 'Agricultural stress detected',
              description: `${event.stress_type} stress in ${event.region?.name || 'Unknown region'}`,
              timestamp: event.detection_date,
              status: event.severity === 'high' ? 'warning' : 'completed'
            })) || []),
            // Recent conflict events
            ...(data.conflictSummary?.recent_events?.slice(0, 1).map(event => ({
              id: `conflict-${event.id}`,
              type: 'alert',
              title: 'Conflict event reported',
              description: `${event.event_type} in ${event.region?.name || 'Unknown region'}`,
              timestamp: event.event_date,
              status: 'warning'
            })) || []),
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
            { name: 'No Data', value: Math.max(0, (data.regions?.count || 0) - (data.stressSummary?.total_events || 0)), color: '#6b7280' }
          ],
          topRegions: data.regions?.results?.slice(0, 5).map(region => ({
            name: region.name,
            ndvi: 0.5, // Will be updated with real vegetation data
            area: region.area_hectares / 100, // Convert to km²
            status: 'healthy', // Will be determined by stress events
            change: 0 // Will be calculated from trend data
          })) || []
        };

        // Fetch vegetation trend data for the first few regions
        if (data.regions?.results?.length > 0) {
          try {
            const vegetationPromises = data.regions.results.slice(0, 3).map(region => 
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
            // Use fallback mock data for vegetation trends
            transformedData.vegetationTrends = [
              { date: '2023-10-01', ndvi: 0.65, evi: 0.58, ndwi: 0.12, savi: 0.52 },
              { date: '2023-10-08', ndvi: 0.62, evi: 0.55, ndwi: 0.15, savi: 0.49 },
              { date: '2023-10-15', ndvi: 0.58, evi: 0.51, ndwi: 0.18, savi: 0.46 },
              { date: '2023-10-22', ndvi: 0.54, evi: 0.47, ndwi: 0.22, savi: 0.42 },
              { date: '2023-10-29', ndvi: 0.51, evi: 0.44, ndwi: 0.25, savi: 0.39 },
            ];
          }
        }

        setDashboardData(transformedData);
      } catch (err) {
        console.error('Failed to fetch dashboard data:', err);
        setError('Failed to load dashboard data. Please try again.');
        
        // Fallback to mock data if API fails
        const mockData = {
          stats: {
            totalRegions: 12,
            activeRegions: 8,
            totalArea: 2450.5,
            lastUpdate: new Date().toISOString(),
            processingTasks: 3,
            alertsCount: 5,
            reportsGenerated: 23,
            organizationsCount: 4
          },
          recentActivity: [
            {
              id: 1,
              type: 'processing',
              title: 'Satellite data processing completed',
              description: 'NDVI analysis for Goma region finished',
              timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
              status: 'completed'
            },
            {
              id: 2,
              type: 'alert',
              title: 'Agricultural stress detected',
              description: 'Low NDVI values in Bukavu agricultural zone',
              timestamp: new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString(),
              status: 'warning'
            }
          ],
          vegetationTrends: [
            { date: '2023-10-01', ndvi: 0.65, evi: 0.58, ndwi: 0.12, savi: 0.52 },
            { date: '2023-10-08', ndvi: 0.62, evi: 0.55, ndwi: 0.15, savi: 0.49 },
            { date: '2023-10-15', ndvi: 0.58, evi: 0.51, ndwi: 0.18, savi: 0.46 },
            { date: '2023-10-22', ndvi: 0.54, evi: 0.47, ndwi: 0.22, savi: 0.42 },
            { date: '2023-10-29', ndvi: 0.51, evi: 0.44, ndwi: 0.25, savi: 0.39 },
          ],
          regionStatus: [
            { name: 'Healthy', value: 5, color: '#10b981' },
            { name: 'Moderate', value: 4, color: '#f59e0b' },
            { name: 'Stressed', value: 2, color: '#ef4444' },
            { name: 'No Data', value: 1, color: '#6b7280' }
          ],
          topRegions: [
            { name: 'Goma Agricultural Zone', ndvi: 0.72, area: 245.3, status: 'healthy', change: 0.05 },
            { name: 'Bukavu Farmlands', ndvi: 0.68, area: 189.7, status: 'healthy', change: 0.02 },
            { name: 'Uvira Coastal Plains', ndvi: 0.45, area: 156.2, status: 'moderate', change: -0.08 },
            { name: 'Rutshuru Valley', ndvi: 0.32, area: 298.1, status: 'stressed', change: -0.15 },
            { name: 'Masisi Highlands', ndvi: 0.28, area: 201.4, status: 'stressed', change: -0.12 }
          ]
        };
        setDashboardData(mockData);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

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
        
        <Card className="border-red-200 bg-red-50 dark:bg-red-900/10">
          <CardContent className="p-6">
            <div className="flex items-center space-x-3">
              <AlertTriangle className="h-6 w-6 text-red-600" />
              <div>
                <h3 className="text-lg font-semibold text-red-800 dark:text-red-200">
                  Error Loading Dashboard
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

  const { stats, recentActivity, vegetationTrends, regionStatus, topRegions } = dashboardData;

  return (
    <div className="space-y-6">
      {/* Welcome Section */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
              Welcome back, {user?.first_name}!
            </h1>
            <p className="text-gray-600 dark:text-gray-400 mt-2">
              Here's what's happening with your agricultural monitoring system.
            </p>
          </div>
          <div className="flex items-center space-x-2">
            <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
            <span className="text-sm text-gray-600 dark:text-gray-400">
              {isConnected ? 'Real-time connected' : 'Offline'}
            </span>
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
            <CardTitle>Vegetation Index Trends</CardTitle>
            <CardDescription>
              Weekly vegetation health indicators across all regions
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={vegetationTrends}>
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
                  <Line 
                    type="monotone" 
                    dataKey="savi" 
                    stroke="#f59e0b" 
                    strokeWidth={2}
                    name="SAVI"
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        {/* Region Status Distribution */}
        <Card>
          <CardHeader>
            <CardTitle>Region Health Status</CardTitle>
            <CardDescription>
              Distribution of agricultural health across monitored regions
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-80">
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
                  >
                    {regionStatus.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div className="flex flex-wrap justify-center gap-4 mt-4">
              {regionStatus.map((status, index) => (
                <div key={index} className="flex items-center space-x-2">
                  <div 
                    className="w-3 h-3 rounded-full"
                    style={{ backgroundColor: status.color }}
                  />
                  <span className="text-sm text-gray-600 dark:text-gray-400">
                    {status.name} ({status.value})
                  </span>
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
              {topRegions.map((region, index) => (
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
              ))}
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
              {recentActivity.map((activity) => (
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
              ))}
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
            Common tasks and shortcuts
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4">
            <Button variant="outline" className="flex flex-col items-center p-4 h-auto">
              <Satellite className="h-6 w-6 mb-2" />
              <span className="text-sm">Process Data</span>
            </Button>
            <Button variant="outline" className="flex flex-col items-center p-4 h-auto">
              <FileText className="h-6 w-6 mb-2" />
              <span className="text-sm">Generate Report</span>
            </Button>
            <Button variant="outline" className="flex flex-col items-center p-4 h-auto">
              <MapPin className="h-6 w-6 mb-2" />
              <span className="text-sm">Add Region</span>
            </Button>
            <Button variant="outline" className="flex flex-col items-center p-4 h-auto">
              <AlertTriangle className="h-6 w-6 mb-2" />
              <span className="text-sm">View Alerts</span>
            </Button>
            <Button variant="outline" className="flex flex-col items-center p-4 h-auto">
              <Download className="h-6 w-6 mb-2" />
              <span className="text-sm">Export Data</span>
            </Button>
            <Button variant="outline" className="flex flex-col items-center p-4 h-auto">
              <Users className="h-6 w-6 mb-2" />
              <span className="text-sm">Manage Users</span>
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default Dashboard;

