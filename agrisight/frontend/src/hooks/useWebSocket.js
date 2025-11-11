import { useEffect, useRef, useState, useCallback } from 'react';

const useWebSocket = (url, options = {}) => {
  const [socket, setSocket] = useState(null);
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState(null);
  const [lastMessage, setLastMessage] = useState(null);
  const reconnectTimeoutRef = useRef(null);
  const reconnectAttempts = useRef(0);
  const maxReconnectAttempts = options.maxReconnectAttempts || 5;
  const reconnectInterval = options.reconnectInterval || 3000;
  const shouldConnect = options.shouldConnect !== false; // Default to true if not specified

  const connect = useCallback(() => {
    // Don't connect if url is null or shouldConnect is false
    if (!url || !shouldConnect) {
      console.log('WebSocket connection skipped - url:', !!url, 'shouldConnect:', shouldConnect);
      return;
    }

    try {
      const ws = new WebSocket(url);
      
      ws.onopen = () => {
        console.log('WebSocket connected');
        setIsConnected(true);
        setError(null);
        reconnectAttempts.current = 0;
        
        // Send authentication if provided
        if (options.authToken) {
          ws.send(JSON.stringify({
            type: 'auth',
            token: options.authToken
          }));
        }
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          setLastMessage(data);
          
          // Call message handler if provided
          if (options.onMessage) {
            options.onMessage(data);
          }
        } catch (err) {
          console.error('Failed to parse WebSocket message:', err);
        }
      };

      ws.onclose = (event) => {
        console.log('WebSocket disconnected:', event.code, event.reason);
        setIsConnected(false);
        
        // Attempt to reconnect if not a normal closure and should connect
        if (event.code !== 1000 && reconnectAttempts.current < maxReconnectAttempts && shouldConnect) {
          reconnectAttempts.current += 1;
          console.log(`Attempting to reconnect (${reconnectAttempts.current}/${maxReconnectAttempts})...`);
          
          reconnectTimeoutRef.current = setTimeout(() => {
            connect();
          }, reconnectInterval * reconnectAttempts.current);
        }
      };

      ws.onerror = (event) => {
        console.error('WebSocket error:', event);
        setError('WebSocket connection error');
        // Don't throw - allow the hook to handle gracefully
      };

      setSocket(ws);
    } catch (err) {
      console.error('Failed to create WebSocket connection:', err);
      setError('Failed to create WebSocket connection');
    }
  }, [url, shouldConnect, options]);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    
    if (socket) {
      socket.close(1000, 'User disconnected');
      setSocket(null);
    }
    
    setIsConnected(false);
  }, [socket]);

  const sendMessage = useCallback((message) => {
    if (socket && isConnected) {
      socket.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket is not connected');
    }
  }, [socket, isConnected]);

  useEffect(() => {
    if (shouldConnect && url) {
      connect();
    }
    
    return () => {
      disconnect();
    };
  }, [shouldConnect, url, connect, disconnect]);

  return {
    socket,
    isConnected,
    error,
    lastMessage,
    sendMessage,
    disconnect,
    reconnect: connect
  };
};

export default useWebSocket;
