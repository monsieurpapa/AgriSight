import { useEffect, useRef, useState, useCallback } from 'react';

const useWebSocket = (url, options = {}) => {
  const [socket, setSocket] = useState(null);
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState(null);
  const [lastMessage, setLastMessage] = useState(null);
  const reconnectTimeoutRef = useRef(null);
  const reconnectAttempts = useRef(0);
  const socketRef = useRef(null);
  const maxReconnectAttempts = options.maxReconnectAttempts || 5;
  const reconnectInterval = options.reconnectInterval || 3000;
  const shouldConnect = options.shouldConnect !== false; // Default to true if not specified
  const authToken = options.authToken;

  // Callers (e.g. WebSocketContext) routinely pass an inline options object and
  // an inline onMessage function, both recreated on every render. Reading them
  // through a ref (rather than putting `options`/`onMessage` in connect's
  // dependency array) keeps `connect` referentially stable across renders so
  // the mount effect below doesn't tear down and reopen the socket on every
  // render — that was causing an unbounded reconnect loop.
  const onMessageRef = useRef(options.onMessage);
  onMessageRef.current = options.onMessage;

  const connect = useCallback(() => {
    // Don't connect if url is null or shouldConnect is false
    if (!url || !shouldConnect) {
      console.log('WebSocket connection skipped - url:', !!url, 'shouldConnect:', shouldConnect);
      return;
    }

    try {
      const ws = new WebSocket(url);
      socketRef.current = ws;

      ws.onopen = () => {
        console.log('WebSocket connected');
        setIsConnected(true);
        setError(null);
        reconnectAttempts.current = 0;

        // Send authentication if provided
        if (authToken) {
          ws.send(JSON.stringify({
            type: 'auth',
            token: authToken
          }));
        }
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          setLastMessage(data);

          // Call message handler if provided
          if (onMessageRef.current) {
            onMessageRef.current(data);
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
  }, [url, shouldConnect, authToken, maxReconnectAttempts, reconnectInterval]);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }

    if (socketRef.current) {
      socketRef.current.close(1000, 'User disconnected');
      socketRef.current = null;
      setSocket(null);
    }

    setIsConnected(false);
  }, []);

  const sendMessage = useCallback((message) => {
    if (socketRef.current && isConnected) {
      socketRef.current.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket is not connected');
    }
  }, [isConnected]);

  useEffect(() => {
    if (shouldConnect && url) {
      connect();
    }

    return () => {
      disconnect();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [shouldConnect, url, connect]);

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
