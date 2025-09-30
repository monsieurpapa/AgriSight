import React, { Suspense, lazy } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import Layout from './components/layout/Layout';
import Dashboard from './pages/Dashboard';
import Login from './pages/Login';
import Landing from './pages/Landing';
import PublicDemo from './pages/PublicDemo';
const MapView = lazy(() => import('./pages/MapView'));
const Regions = lazy(() => import('./pages/Regions'));
const SatelliteData = lazy(() => import('./pages/SatelliteData'));
const VegetationIndices = lazy(() => import('./pages/VegetationIndices'));
const Analytics = lazy(() => import('./pages/Analytics'));
const StressEvents = lazy(() => import('./pages/StressEvents'));
const Alerts = lazy(() => import('./pages/Alerts'));
const Reports = lazy(() => import('./pages/Reports'));
const Exports = lazy(() => import('./pages/Exports'));
const Organizations = lazy(() => import('./pages/Organizations'));
const AdminSettings = lazy(() => import('./pages/AdminSettings'));
const AdminPerformance = lazy(() => import('./pages/AdminPerformance'));
const Profile = lazy(() => import('./pages/Profile'));
const Settings = lazy(() => import('./pages/Settings'));
const Register = lazy(() => import('./pages/Register'));
const ForgotPassword = lazy(() => import('./pages/ForgotPassword'));
const Privacy = lazy(() => import('./pages/Privacy'));
const Terms = lazy(() => import('./pages/Terms'));
const Support = lazy(() => import('./pages/Support'));
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
    return <Navigate to="/landing" replace />;
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
// Route-level fallback
const Fallback = () => (
  <div className="min-h-[200px] flex items-center justify-center">
    <div className="text-center">
      <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-green-600 mx-auto"></div>
      <p className="mt-3 text-gray-600 dark:text-gray-400">Loading...</p>
    </div>
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
            <Route path="/landing" element={<Landing />} />
            <Route path="/demo" element={<PublicDemo />} />
              <Route path="/login" element={
                <PublicRoute>
                  <Login />
                </PublicRoute>
              } />
              <Route path="/register" element={
                <PublicRoute>
                  <Suspense fallback={<Fallback />}>
                    <Register />
                  </Suspense>
                </PublicRoute>
              } />
              <Route path="/forgot-password" element={
                <PublicRoute>
                  <Suspense fallback={<Fallback />}>
                    <ForgotPassword />
                  </Suspense>
                </PublicRoute>
              } />
              <Route path="/privacy" element={
                <Suspense fallback={<Fallback />}>
                  <Privacy />
                </Suspense>
              } />
              <Route path="/terms" element={
                <Suspense fallback={<Fallback />}>
                  <Terms />
                </Suspense>
              } />
              <Route path="/support" element={
                <Suspense fallback={<Fallback />}>
                  <Support />
                </Suspense>
              } />

              {/* Protected routes */}
              <Route element={
                <ProtectedRoute>
                  <Layout />
                </ProtectedRoute>
              }>
                <Route path="/" element={<Dashboard />} />
                <Route path="/map" element={
                  <Suspense fallback={<Fallback />}>
                    <MapView />
                  </Suspense>
                } />
                <Route path="/regions" element={
                  <Suspense fallback={<Fallback />}>
                    <Regions />
                  </Suspense>
                } />
                <Route path="/satellite" element={
                  <Suspense fallback={<Fallback />}>
                    <SatelliteData />
                  </Suspense>
                } />
                <Route path="/vegetation" element={
                  <Suspense fallback={<Fallback />}>
                    <VegetationIndices />
                  </Suspense>
                } />
                <Route path="/analytics" element={
                  <Suspense fallback={<Fallback />}>
                    <Analytics />
                  </Suspense>
                } />
                <Route path="/stress-events" element={
                  <Suspense fallback={<Fallback />}>
                    <StressEvents />
                  </Suspense>
                } />
                <Route path="/alerts" element={
                  <Suspense fallback={<Fallback />}>
                    <Alerts />
                  </Suspense>
                } />
                <Route path="/reports" element={
                  <Suspense fallback={<Fallback />}>
                    <Reports />
                  </Suspense>
                } />
                <Route path="/exports" element={
                  <Suspense fallback={<Fallback />}>
                    <Exports />
                  </Suspense>
                } />
                <Route path="/organizations" element={
                  <Suspense fallback={<Fallback />}>
                    <Organizations />
                  </Suspense>
                } />
                <Route path="/admin/settings" element={
                  <Suspense fallback={<Fallback />}>
                    <AdminSettings />
                  </Suspense>
                } />
                <Route path="/admin/performance" element={
                  <Suspense fallback={<Fallback />}>
                    <AdminPerformance />
                  </Suspense>
                } />
                <Route path="/profile" element={
                  <Suspense fallback={<Fallback />}>
                    <Profile />
                  </Suspense>
                } />
                <Route path="/settings" element={
                  <Suspense fallback={<Fallback />}>
                    <Settings />
                  </Suspense>
                } />
              </Route>

              {/* Catch all route */}
              <Route path="*" element={
                <Navigate to="/landing" replace />
              } />
            </Routes>
          </div>
        </Router>
      </AuthProvider>
    </QueryClientProvider>
  );
}

export default App;