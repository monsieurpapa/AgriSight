import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import Layout from './components/layout/Layout';
import Dashboard from './pages/Dashboard';
import Login from './pages/Login';
import './App.css';

// Create a query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

// Protected Route component
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600 mx-auto"></div>
          <p className="mt-4 text-gray-600 dark:text-gray-400">Loading...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return children;
};

// Public Route component (redirects to dashboard if authenticated)
const PublicRoute = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600 mx-auto"></div>
          <p className="mt-4 text-gray-600 dark:text-gray-400">Loading...</p>
        </div>
      </div>
    );
  }

  if (isAuthenticated) {
    return <Navigate to="/" replace />;
  }

  return children;
};

// Placeholder components for other pages
const MapView = () => (
  <div className="text-center py-12">
    <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
      Interactive Map View
    </h1>
    <p className="text-gray-600 dark:text-gray-400">
      Satellite imagery and vegetation index overlays will be displayed here.
    </p>
  </div>
);

const Regions = () => (
  <div className="text-center py-12">
    <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
      Regions Management
    </h1>
    <p className="text-gray-600 dark:text-gray-400">
      Manage and monitor agricultural regions in DRC.
    </p>
  </div>
);

const SatelliteData = () => (
  <div className="text-center py-12">
    <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
      Satellite Data Processing
    </h1>
    <p className="text-gray-600 dark:text-gray-400">
      View and process Sentinel-2 satellite imagery.
    </p>
  </div>
);

const VegetationIndices = () => (
  <div className="text-center py-12">
    <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
      Vegetation Indices
    </h1>
    <p className="text-gray-600 dark:text-gray-400">
      NDVI, EVI, NDWI, and SAVI analysis and trends.
    </p>
  </div>
);

const Analytics = () => (
  <div className="text-center py-12">
    <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
      Advanced Analytics
    </h1>
    <p className="text-gray-600 dark:text-gray-400">
      Deep insights and predictive analysis.
    </p>
  </div>
);

const StressEvents = () => (
  <div className="text-center py-12">
    <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
      Agricultural Stress Events
    </h1>
    <p className="text-gray-600 dark:text-gray-400">
      Monitor and manage agricultural stress events and anomalies.
    </p>
  </div>
);

const Alerts = () => (
  <div className="text-center py-12">
    <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
      Alerts & Notifications
    </h1>
    <p className="text-gray-600 dark:text-gray-400">
      System alerts and notification management.
    </p>
  </div>
);

const Reports = () => (
  <div className="text-center py-12">
    <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
      Reports & Documentation
    </h1>
    <p className="text-gray-600 dark:text-gray-400">
      Generate and view agricultural monitoring reports.
    </p>
  </div>
);

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <Router>
          <div className="App">
            <Routes>
              {/* Public routes */}
              <Route
                path="/login"
                element={
                  <PublicRoute>
                    <Login />
                  </PublicRoute>
                }
              />

              {/* Protected routes */}
              <Route
                path="/"
                element={
                  <ProtectedRoute>
                    <Layout />
                  </ProtectedRoute>
                }
              >
                <Route index element={<Dashboard />} />
                <Route path="map" element={<MapView />} />
                <Route path="regions" element={<Regions />} />
                <Route path="satellite" element={<SatelliteData />} />
                <Route path="vegetation" element={<VegetationIndices />} />
                <Route path="analytics" element={<Analytics />} />
                <Route path="stress-events" element={<StressEvents />} />
                <Route path="alerts" element={<Alerts />} />
                <Route path="reports" element={<Reports />} />
              </Route>

              {/* Catch all route */}
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </div>
        </Router>
      </AuthProvider>
    </QueryClientProvider>
  );
}

export default App;
