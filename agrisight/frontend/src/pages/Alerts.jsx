import React, { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { alertsAPI, analyticsAPI, satelliteProcessingAPI } from '../lib/api';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { Switch } from '../components/ui/switch';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { 
  Bell, 
  Check, 
  RefreshCcw, 
  AlertTriangle, 
  Activity, 
  Settings, 
  Eye, 
  EyeOff,
  Zap,
  Shield,
  Clock,
  MapPin,
  TrendingUp,
  TrendingDown,
  Filter,
  Download,
  Volume2,
  VolumeX
} from 'lucide-react';
import { useWebSocketContext } from '../contexts/WebSocketContext';
import { formatDate, formatRelativeTime } from '../lib/utils';

const Alerts = () => {
  const { isConnected, realTimeData, notifications } = useWebSocketContext();
  const [alertSettings, setAlertSettings] = useState({
    stressAlerts: true,
    conflictAlerts: true,
    systemAlerts: true,
    processingAlerts: false,
    soundEnabled: true,
    emailNotifications: true,
    severityFilter: 'all'
  });
  const [systemHealth, setSystemHealth] = useState({
    status: 'healthy',
    uptime: '99.9%',
    responseTime: '120ms',
    activeConnections: 45,
    lastUpdate: new Date().toISOString()
  });

  const { data, isLoading, isError, refetch, isFetching } = useQuery({
    queryKey: ['alerts'],
    queryFn: () => alertsAPI.getAlerts(),
    refetchInterval: 30000, // Refetch every 30 seconds
  });

  // Real-time system health monitoring
  useEffect(() => {
    const updateSystemHealth = () => {
      setSystemHealth(prev => ({
        ...prev,
        lastUpdate: new Date().toISOString(),
        activeConnections: Math.floor(Math.random() * 20) + 40, // Simulate connection count
        responseTime: `${Math.floor(Math.random() * 50) + 100}ms` // Simulate response time
      }));
    };

    const interval = setInterval(updateSystemHealth, 10000); // Update every 10 seconds
    return () => clearInterval(interval);
  }, []);

  // Handle real-time notifications
  useEffect(() => {
    if (notifications && notifications.length > 0) {
      // Play sound if enabled
      if (alertSettings.soundEnabled) {
        // Simple notification sound (in a real app, you'd use a proper audio file)
        console.log('🔔 New notification received');
      }
    }
  }, [notifications, alertSettings.soundEnabled]);

  const handleMarkAsRead = (alertId) => {
    // In a real app, this would call an API to mark the alert as read
    console.log('Marking alert as read:', alertId);
  };

  const handleAlertSettingsChange = (setting, value) => {
    setAlertSettings(prev => ({
      ...prev,
      [setting]: value
    }));
  };

  const getAlertIcon = (type, severity) => {
    switch (type) {
      case 'stress':
        return <AlertTriangle className="h-4 w-4 text-red-600" />;
      case 'conflict':
        return <Shield className="h-4 w-4 text-orange-600" />;
      case 'system':
        return <Activity className="h-4 w-4 text-blue-600" />;
      case 'processing':
        return <Zap className="h-4 w-4 text-purple-600" />;
      default:
        return <Bell className="h-4 w-4 text-gray-600" />;
    }
  };

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'high':
        return 'border-red-500 text-red-700 bg-red-50 dark:bg-red-900/10';
      case 'medium':
        return 'border-yellow-500 text-yellow-700 bg-yellow-50 dark:bg-yellow-900/10';
      case 'low':
        return 'border-green-500 text-green-700 bg-green-50 dark:bg-green-900/10';
      default:
        return 'border-gray-500 text-gray-700 bg-gray-50 dark:bg-gray-900/10';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Alerts & Monitoring</h1>
          <p className="text-gray-600 dark:text-gray-400">
            Real-time system monitoring and alert management
            {isConnected && (
              <span className="ml-2 inline-flex items-center gap-1 text-green-600">
                <div className="w-2 h-2 rounded-full bg-green-500"></div>
                Live
              </span>
            )}
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => refetch()} disabled={isFetching}>
            <RefreshCcw className={`h-4 w-4 mr-2 ${isFetching ? 'animate-spin' : ''}`}/>
            Refresh
          </Button>
          <Button variant="outline">
            <Download className="h-4 w-4 mr-2"/>
            Export
          </Button>
        </div>
      </div>

      {/* System Health Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">System Status</p>
                <p className="text-2xl font-bold text-green-600 dark:text-green-400">
                  {systemHealth.status === 'healthy' ? 'Healthy' : 'Warning'}
                </p>
              </div>
              <div className="w-10 h-10 bg-green-100 dark:bg-green-900/20 rounded-lg flex items-center justify-center">
                <Shield className="h-5 w-5 text-green-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Uptime</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">{systemHealth.uptime}</p>
              </div>
              <div className="w-10 h-10 bg-blue-100 dark:bg-blue-900/20 rounded-lg flex items-center justify-center">
                <Clock className="h-5 w-5 text-blue-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Response Time</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">{systemHealth.responseTime}</p>
              </div>
              <div className="w-10 h-10 bg-purple-100 dark:bg-purple-900/20 rounded-lg flex items-center justify-center">
                <Zap className="h-5 w-5 text-purple-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Active Connections</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">{systemHealth.activeConnections}</p>
              </div>
              <div className="w-10 h-10 bg-orange-100 dark:bg-orange-900/20 rounded-lg flex items-center justify-center">
                <Activity className="h-5 w-5 text-orange-600" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Main Content Tabs */}
      <Tabs defaultValue="alerts" className="space-y-6">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="alerts">Active Alerts</TabsTrigger>
          <TabsTrigger value="notifications">Real-time Notifications</TabsTrigger>
          <TabsTrigger value="monitoring">System Monitoring</TabsTrigger>
          <TabsTrigger value="settings">Alert Settings</TabsTrigger>
        </TabsList>

        {/* Active Alerts Tab */}
        <TabsContent value="alerts" className="space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Active Alerts</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                {data?.results?.length || 0} active alerts requiring attention
              </p>
            </div>
            <div className="flex gap-2">
              <Select value={alertSettings.severityFilter} onValueChange={(value) => handleAlertSettingsChange('severityFilter', value)}>
                <SelectTrigger className="w-32">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Severity</SelectItem>
                  <SelectItem value="high">High Only</SelectItem>
                  <SelectItem value="medium">Medium+</SelectItem>
                  <SelectItem value="low">All Levels</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <Card>
            <CardContent className="p-0">
              {isLoading ? (
                <div className="py-12 text-center text-gray-600 dark:text-gray-400">
                  <Activity className="h-8 w-8 mx-auto mb-2 animate-spin" />
                  Loading alerts...
                </div>
              ) : isError ? (
                <div className="py-12 text-center text-red-600">
                  <AlertTriangle className="h-8 w-8 mx-auto mb-2" />
                  Failed to load alerts. Please try again.
                </div>
              ) : data?.results?.length ? (
                <div className="divide-y divide-gray-200 dark:divide-gray-700">
                  {data.results.map((alert) => (
                    <div key={alert.id} className="p-4 hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors">
                      <div className="flex items-start justify-between">
                        <div className="flex items-start gap-3 flex-1">
                          <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                            alert.severity === 'high' ? 'bg-red-100 dark:bg-red-900/20' :
                            alert.severity === 'medium' ? 'bg-yellow-100 dark:bg-yellow-900/20' :
                            'bg-green-100 dark:bg-green-900/20'
                          }`}>
                            {getAlertIcon(alert.type || 'system', alert.severity)}
                          </div>
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-1">
                              <h4 className="font-medium text-gray-900 dark:text-white">
                                {alert.title || 'System Alert'}
                              </h4>
                              <Badge variant="outline" className={getSeverityColor(alert.severity)}>
                                {alert.severity || 'info'}
                              </Badge>
                            </div>
                            <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                              {alert.message || alert.description || 'No description available'}
                            </p>
                            <div className="flex items-center gap-4 text-xs text-gray-500 dark:text-gray-400">
                              <span className="flex items-center gap-1">
                                <Clock className="h-3 w-3" />
                                {formatRelativeTime(alert.created_at || alert.timestamp)}
                              </span>
                              {alert.region && (
                                <span className="flex items-center gap-1">
                                  <MapPin className="h-3 w-3" />
                                  {alert.region.name}
                                </span>
                              )}
                            </div>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          <Button 
                            variant="outline" 
                            size="sm"
                            onClick={() => handleMarkAsRead(alert.id)}
                          >
                            <Check className="h-4 w-4 mr-1"/>
                            Mark Read
                          </Button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="py-12 text-center">
                  <div className="mx-auto w-12 h-12 rounded-full bg-green-100 dark:bg-green-900/20 flex items-center justify-center">
                    <Bell className="h-6 w-6 text-green-600"/>
                  </div>
                  <p className="mt-3 text-gray-900 dark:text-white font-medium">All Clear!</p>
                  <p className="text-gray-600 dark:text-gray-400">No active alerts at this time.</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Real-time Notifications Tab */}
        <TabsContent value="notifications" className="space-y-6">
          <div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Real-time Notifications</h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Live notifications from WebSocket connection
            </p>
          </div>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Bell className="h-5 w-5" />
                Recent Notifications
                {notifications && notifications.length > 0 && (
                  <Badge variant="secondary">{notifications.length}</Badge>
                )}
              </CardTitle>
            </CardHeader>
            <CardContent>
              {notifications && notifications.length > 0 ? (
                <div className="space-y-3">
                  {notifications.slice(0, 10).map((notification, index) => (
                    <div key={notification.id || index} className={`p-3 rounded-lg border ${
                      notification.type === 'alert' ? 'border-red-200 bg-red-50 dark:bg-red-900/10' :
                      notification.type === 'warning' ? 'border-yellow-200 bg-yellow-50 dark:bg-yellow-900/10' :
                      'border-blue-200 bg-blue-50 dark:bg-blue-900/10'
                    }`}>
                      <div className="flex items-start gap-3">
                        <div className={`w-6 h-6 rounded-full flex items-center justify-center ${
                          notification.type === 'alert' ? 'bg-red-100 dark:bg-red-900/20' :
                          notification.type === 'warning' ? 'bg-yellow-100 dark:bg-yellow-900/20' :
                          'bg-blue-100 dark:bg-blue-900/20'
                        }`}>
                          <Bell className={`h-3 w-3 ${
                            notification.type === 'alert' ? 'text-red-600' :
                            notification.type === 'warning' ? 'text-yellow-600' :
                            'text-blue-600'
                          }`} />
                        </div>
                        <div className="flex-1">
                          <p className="text-sm font-medium text-gray-900 dark:text-white">
                            {notification.message}
                          </p>
                          <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                            {formatRelativeTime(notification.timestamp)}
                          </p>
                        </div>
                        {!notification.read && (
                          <div className="w-2 h-2 rounded-full bg-red-500"></div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500 dark:text-gray-400">
                  <Bell className="h-8 w-8 mx-auto mb-2" />
                  <p>No recent notifications</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* System Monitoring Tab */}
        <TabsContent value="monitoring" className="space-y-6">
          <div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">System Monitoring</h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Real-time system performance and health metrics
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Performance Metrics</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600 dark:text-gray-400">CPU Usage</span>
                  <span className="text-sm font-medium">23%</span>
                </div>
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                  <div className="bg-green-500 h-2 rounded-full" style={{ width: '23%' }}></div>
                </div>

                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600 dark:text-gray-400">Memory Usage</span>
                  <span className="text-sm font-medium">67%</span>
                </div>
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                  <div className="bg-yellow-500 h-2 rounded-full" style={{ width: '67%' }}></div>
                </div>

                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600 dark:text-gray-400">Disk Usage</span>
                  <span className="text-sm font-medium">45%</span>
                </div>
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                  <div className="bg-blue-500 h-2 rounded-full" style={{ width: '45%' }}></div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Network Status</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600 dark:text-gray-400">WebSocket Connection</span>
                  <div className="flex items-center gap-2">
                    <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`}></div>
                    <span className="text-sm font-medium">{isConnected ? 'Connected' : 'Disconnected'}</span>
                  </div>
                </div>

                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600 dark:text-gray-400">API Response Time</span>
                  <span className="text-sm font-medium">{systemHealth.responseTime}</span>
                </div>

                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600 dark:text-gray-400">Active Users</span>
                  <span className="text-sm font-medium">{systemHealth.activeConnections}</span>
                </div>

                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600 dark:text-gray-400">Last Update</span>
                  <span className="text-sm font-medium">{formatRelativeTime(systemHealth.lastUpdate)}</span>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Alert Settings Tab */}
        <TabsContent value="settings" className="space-y-6">
          <div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Alert Settings</h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Configure your notification preferences and alert types
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Alert Types</CardTitle>
                <CardDescription>Choose which types of alerts you want to receive</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium text-gray-900 dark:text-white">Stress Alerts</p>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Agricultural stress events</p>
                  </div>
                  <Switch
                    checked={alertSettings.stressAlerts}
                    onCheckedChange={(checked) => handleAlertSettingsChange('stressAlerts', checked)}
                  />
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium text-gray-900 dark:text-white">Conflict Alerts</p>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Security and conflict events</p>
                  </div>
                  <Switch
                    checked={alertSettings.conflictAlerts}
                    onCheckedChange={(checked) => handleAlertSettingsChange('conflictAlerts', checked)}
                  />
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium text-gray-900 dark:text-white">System Alerts</p>
                    <p className="text-sm text-gray-600 dark:text-gray-400">System health and performance</p>
                  </div>
                  <Switch
                    checked={alertSettings.systemAlerts}
                    onCheckedChange={(checked) => handleAlertSettingsChange('systemAlerts', checked)}
                  />
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium text-gray-900 dark:text-white">Processing Alerts</p>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Data processing notifications</p>
                  </div>
                  <Switch
                    checked={alertSettings.processingAlerts}
                    onCheckedChange={(checked) => handleAlertSettingsChange('processingAlerts', checked)}
                  />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Notification Preferences</CardTitle>
                <CardDescription>Configure how you receive notifications</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium text-gray-900 dark:text-white">Sound Notifications</p>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Play sound for new alerts</p>
                  </div>
                  <Switch
                    checked={alertSettings.soundEnabled}
                    onCheckedChange={(checked) => handleAlertSettingsChange('soundEnabled', checked)}
                  />
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium text-gray-900 dark:text-white">Email Notifications</p>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Send email alerts</p>
                  </div>
                  <Switch
                    checked={alertSettings.emailNotifications}
                    onCheckedChange={(checked) => handleAlertSettingsChange('emailNotifications', checked)}
                  />
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                    Minimum Severity Level
                  </label>
                  <Select value={alertSettings.severityFilter} onValueChange={(value) => handleAlertSettingsChange('severityFilter', value)}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Levels</SelectItem>
                      <SelectItem value="high">High Only</SelectItem>
                      <SelectItem value="medium">Medium and High</SelectItem>
                      <SelectItem value="low">All Levels</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default Alerts;


