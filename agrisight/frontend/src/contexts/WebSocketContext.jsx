import React, { createContext, useContext, useEffect, useState } from 'react';
import useWebSocket from '../hooks/useWebSocket';
import { useAuth } from './AuthContext';

const WebSocketContext = createContext();

export const useWebSocketContext = () => {
  const context = useContext(WebSocketContext);
  if (!context) {
    throw new Error('useWebSocketContext must be used within a WebSocketProvider');
  }
  return context;
};

export const WebSocketProvider = ({ children }) => {
  const { user, isAuthenticated } = useAuth();
  const [notifications, setNotifications] = useState([]);
  const [realTimeData, setRealTimeData] = useState({
    stressEvents: [],
    processingTasks: [],
    systemAlerts: []
  });

  // WebSocket URL - adjust based on environment
  const wsUrl = import.meta.env.VITE_WS_URL || 
    (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000')
      .replace('http://', 'ws://')
      .replace('https://', 'wss://') + '/ws/';

  // Only connect WebSocket if authenticated
  const { isConnected, error, sendMessage, lastMessage } = useWebSocket(
    isAuthenticated ? wsUrl : null,
    {
      authToken: user?.sessionid, // Use session ID for authentication
      onMessage: handleWebSocketMessage,
      maxReconnectAttempts: 5,
      reconnectInterval: 3000,
      shouldConnect: isAuthenticated // Only connect when authenticated
    }
  );

  function handleWebSocketMessage(data) {
    console.log('WebSocket message received:', data);
    
    switch (data.type) {
      case 'stress_event':
        setRealTimeData(prev => ({
          ...prev,
          stressEvents: [data.payload, ...prev.stressEvents.slice(0, 9)] // Keep last 10
        }));
        addNotification({
          id: `stress-${data.payload.id}`,
          type: 'stress',
          title: 'Agricultural Stress Detected',
          message: `${data.payload.stress_type} stress in ${data.payload.region?.name || 'Unknown region'}`,
          severity: data.payload.severity,
          timestamp: new Date().toISOString()
        });
        break;
        
      case 'processing_update':
        setRealTimeData(prev => ({
          ...prev,
          processingTasks: prev.processingTasks.map(task => 
            task.id === data.payload.task_id 
              ? { ...task, status: data.payload.status, progress: data.payload.progress }
              : task
          )
        }));
        break;
        
      case 'system_alert':
        setRealTimeData(prev => ({
          ...prev,
          systemAlerts: [data.payload, ...prev.systemAlerts.slice(0, 9)] // Keep last 10
        }));
        addNotification({
          id: `alert-${data.payload.id}`,
          type: 'system',
          title: 'System Alert',
          message: data.payload.message,
          severity: data.payload.severity,
          timestamp: new Date().toISOString()
        });
        break;
        
      case 'vegetation_update':
        // Handle vegetation index updates
        addNotification({
          id: `vegetation-${data.payload.region_id}`,
          type: 'vegetation',
          title: 'Vegetation Data Updated',
          message: `New ${data.payload.index_type} data for ${data.payload.region_name}`,
          severity: 'info',
          timestamp: new Date().toISOString()
        });
        break;
        
      case 'conflict_event':
        setRealTimeData(prev => ({
          ...prev,
          conflictEvents: [data.payload, ...(prev.conflictEvents || []).slice(0, 9)]
        }));
        addNotification({
          id: `conflict-${data.payload.id}`,
          type: 'conflict',
          title: 'Conflict Event Reported',
          message: `${data.payload.event_type} in ${data.payload.region?.name || 'Unknown region'}`,
          severity: 'high',
          timestamp: new Date().toISOString()
        });
        break;
        
      default:
        console.log('Unknown WebSocket message type:', data.type);
    }
  }

  const addNotification = (notification) => {
    setNotifications(prev => [notification, ...prev.slice(0, 19)]); // Keep last 20 notifications
  };

  const removeNotification = (id) => {
    setNotifications(prev => prev.filter(notif => notif.id !== id));
  };

  const clearNotifications = () => {
    setNotifications([]);
  };

  const subscribeToRegion = (regionId) => {
    sendMessage({
      type: 'subscribe',
      channel: 'region_updates',
      region_id: regionId
    });
  };

  const unsubscribeFromRegion = (regionId) => {
    sendMessage({
      type: 'unsubscribe',
      channel: 'region_updates',
      region_id: regionId
    });
  };

  const subscribeToProcessing = (taskId) => {
    sendMessage({
      type: 'subscribe',
      channel: 'processing_updates',
      task_id: taskId
    });
  };

  const unsubscribeFromProcessing = (taskId) => {
    sendMessage({
      type: 'unsubscribe',
      channel: 'processing_updates',
      task_id: taskId
    });
  };

  // Subscribe to general updates when connected
  useEffect(() => {
    if (isConnected && isAuthenticated) {
      sendMessage({
        type: 'subscribe',
        channel: 'general_updates'
      });
    }
  }, [isConnected, isAuthenticated, sendMessage]);

  const value = {
    isConnected,
    error,
    notifications,
    realTimeData,
    addNotification,
    removeNotification,
    clearNotifications,
    subscribeToRegion,
    unsubscribeFromRegion,
    subscribeToProcessing,
    unsubscribeFromProcessing,
    sendMessage
  };

  return (
    <WebSocketContext.Provider value={value}>
      {children}
    </WebSocketContext.Provider>
  );
};
