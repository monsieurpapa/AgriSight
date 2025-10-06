import apiClient from './apiClient';

// Use the enhanced API client with comprehensive error handling
const { get, post, put, patch, delete: del, upload, download } = apiClient;

export const regionsAPI = {
  getRegions() {
    return get('/api/v1/geospatial/regions/');
  },
  getRegion(id) {
    return get(`/api/v1/geospatial/regions/${id}/`);
  },
};

export const alertsAPI = {
  getAlerts(params = {}) {
    const queryParams = new URLSearchParams(params).toString();
    return get(`/api/v1/reports-alerts/alerts/${queryParams ? '?' + queryParams : ''}`);
  },
  getAlert(id) {
    return get(`/api/v1/reports-alerts/alerts/${id}/`);
  },
  markAlertAsRead(id) {
    return post(`/api/v1/reports-alerts/alerts/${id}/mark-read/`);
  },
  markAllAlertsAsRead() {
    return post('/api/v1/reports-alerts/alerts/mark-all-read/');
  },
  getUnreadCount() {
    return get('/api/v1/reports-alerts/alerts/unread-count/');
  },
  getRecentAlerts() {
    return get('/api/v1/reports-alerts/alerts/recent/');
  }
};

export const reportsAPI = {
  getReports(params = {}) {
    const queryParams = new URLSearchParams(params).toString();
    return get(`/api/v1/reports-alerts/reports/${queryParams ? '?' + queryParams : ''}`);
  },
  getReport(id) {
    return get(`/api/v1/reports-alerts/reports/${id}/`);
  },
  createReport(payload) {
    return post('/api/v1/reports-alerts/reports/', payload);
  },
  updateReport(id, payload) {
    return put(`/api/v1/reports-alerts/reports/${id}/`, payload);
  },
  deleteReport(id) {
    return del(`/api/v1/reports-alerts/reports/${id}/`);
  },
  downloadReport(id) {
    return download(`/api/v1/reports-alerts/reports/${id}/download/`);
  }
};

export const organizationsAPI = {
  getOrganizations() {
    return get('/api/v1/organizations/');
  },
  getOrganization(id) {
    return get(`/api/v1/organizations/${id}/`);
  },
  getCurrentOrganization() {
    return get('/api/v1/organizations/current/');
  },
  createOrganization(payload) {
    return post('/api/v1/organizations/', payload);
  },
  updateOrganization(id, payload) {
    return put(`/api/v1/organizations/${id}/`, payload);
  },
  deleteOrganization(id) {
    return del(`/api/v1/organizations/${id}/`);
  },
  getSubscriptionPlans() {
    return get('/api/v1/organizations/subscription-plans/');
  },
  getSubscriptionPlan(id) {
    return get(`/api/v1/organizations/subscription-plans/${id}/`);
  }
};

// Satellite Processing API
export const satelliteProcessingAPI = {
  // Trigger satellite data processing
  triggerProcessing(payload) {
    return post('/api/v1/satellite-processing/process/', payload);
  },
  
  // Get processing status
  getProcessingStatus(taskId) {
    return get(`/api/v1/satellite-processing/status/${taskId}/`);
  },
  
  // Get vegetation data for a region
  getRegionVegetationData(regionId, params = {}) {
    const queryParams = new URLSearchParams(params).toString();
    return get(`/api/v1/satellite-processing/vegetation/${regionId}/${queryParams ? '?' + queryParams : ''}`);
  },
  
  // Manual data ingestion
  manualDataIngestion(payload) {
    return post('/api/v1/satellite-processing/ingest/', payload);
  },
  
  // Get trend analysis
  getTrendAnalysis(params = {}) {
    const queryParams = new URLSearchParams(params).toString();
    return get(`/api/v1/satellite-processing/trend-analysis/${queryParams ? '?' + queryParams : ''}`);
  },
  
  // Get processing statistics
  getProcessingStatistics() {
    return get('/api/v1/satellite-processing/statistics/');
  },
  
  // Get satellite image details
  getSatelliteImageDetails(imageId) {
    return get(`/api/v1/satellite-processing/image/${imageId}/`);
  }
};

// Analytics API
export const analyticsAPI = {
  // Get stress events
  getStressEvents(params = {}) {
    const queryParams = new URLSearchParams(params).toString();
    return get(`/api/v1/analytics/stress-events/${queryParams ? '?' + queryParams : ''}`);
  },
  
  // Get stress event summary
  getStressEventSummary(params = {}) {
    const queryParams = new URLSearchParams(params).toString();
    return get(`/api/v1/analytics/stress-events/summary/${queryParams ? '?' + queryParams : ''}`);
  },
  
  // Get conflict events
  getConflictEvents(params = {}) {
    const queryParams = new URLSearchParams(params).toString();
    return get(`/api/v1/analytics/conflict-events/${queryParams ? '?' + queryParams : ''}`);
  },
  
  // Get conflict event summary
  getConflictEventSummary(params = {}) {
    const queryParams = new URLSearchParams(params).toString();
    return get(`/api/v1/analytics/conflict-events/summary/${queryParams ? '?' + queryParams : ''}`);
  }
};

// Geospatial API (enhanced)
export const geospatialAPI = {
  // Regions
  getRegions() {
    return get('/api/v1/geospatial/regions/');
  },
  getRegion(id) {
    return get(`/api/v1/geospatial/regions/${id}/`);
  },
  
  // Vegetation indices
  getVegetationIndices(params = {}) {
    const queryParams = new URLSearchParams(params).toString();
    return get(`/api/v1/geospatial/vegetation-indices/${queryParams ? '?' + queryParams : ''}`);
  },
  
  // Satellite images
  getSatelliteImages(params = {}) {
    const queryParams = new URLSearchParams(params).toString();
    return get(`/api/v1/geospatial/satellite-images/${queryParams ? '?' + queryParams : ''}`);
  },
  
  // Crops
  getCrops() {
    return get('/api/v1/geospatial/crops/');
  }
};

// Dashboard API - consolidated endpoint for dashboard data
export const dashboardAPI = {
  // Get comprehensive dashboard data
  getDashboardData() {
    return Promise.all([
      satelliteProcessingAPI.getProcessingStatistics(),
      analyticsAPI.getStressEventSummary({ days: 30 }),
      analyticsAPI.getConflictEventSummary({ days: 30 }),
      geospatialAPI.getRegions(),
      alertsAPI.getAlerts(),
      reportsAPI.getReports()
    ]).then(([processingStats, stressSummary, conflictSummary, regions, alerts, reports]) => {
      return {
        processingStats,
        stressSummary,
        conflictSummary,
        regions,
        alerts,
        reports,
        lastUpdate: new Date().toISOString()
      };
    });
  }
};

// Users API
export const usersAPI = {
  getUsers(params = {}) {
    const queryParams = new URLSearchParams(params).toString();
    return get(`/api/v1/users/${queryParams ? '?' + queryParams : ''}`);
  },
  getUser(id) {
    return get(`/api/v1/users/${id}/`);
  },
  getCurrentUser() {
    return get('/api/v1/users/me/');
  },
  updateCurrentUser(payload) {
    return patch('/api/v1/users/me/update/', payload);
  },
  createUser(payload) {
    return post('/api/v1/users/', payload);
  },
  updateUser(id, payload) {
    return put(`/api/v1/users/${id}/`, payload);
  },
  deleteUser(id) {
    return del(`/api/v1/users/${id}/`);
  }
};

// ML Models API
export const mlModelsAPI = {
  getModels(params = {}) {
    const queryParams = new URLSearchParams(params).toString();
    return get(`/api/v1/ml-models/models/${queryParams ? '?' + queryParams : ''}`);
  },
  getModel(id) {
    return get(`/api/v1/ml-models/models/${id}/`);
  },
  createModel(payload) {
    return post('/api/v1/ml-models/models/', payload);
  },
  updateModel(id, payload) {
    return put(`/api/v1/ml-models/models/${id}/`, payload);
  },
  deleteModel(id) {
    return del(`/api/v1/ml-models/models/${id}/`);
  },
  startTraining(id) {
    return post(`/api/v1/ml-models/models/${id}/train/`);
  },
  makePrediction(id, payload) {
    return post(`/api/v1/ml-models/models/${id}/predict/`, payload);
  },
  getModelPerformance(id) {
    return get(`/api/v1/ml-models/models/${id}/performance/`);
  },
  getTrainingJobs(params = {}) {
    const queryParams = new URLSearchParams(params).toString();
    return get(`/api/v1/ml-models/training-jobs/${queryParams ? '?' + queryParams : ''}`);
  },
  getTrainingJob(id) {
    return get(`/api/v1/ml-models/training-jobs/${id}/`);
  },
  getTrainingStatus(id) {
    return get(`/api/v1/ml-models/training-jobs/${id}/status/`);
  },
  getPredictions(params = {}) {
    const queryParams = new URLSearchParams(params).toString();
    return get(`/api/v1/ml-models/predictions/${queryParams ? '?' + queryParams : ''}`);
  },
  getPrediction(id) {
    return get(`/api/v1/ml-models/predictions/${id}/`);
  },
  compareModels(payload) {
    return post('/api/v1/ml-models/compare-models/', payload);
  },
  getFeatureImportance(modelId) {
    return get(`/api/v1/ml-models/feature-importance/${modelId}/`);
  }
};

// API Keys and Logs API
export const apiKeysAPI = {
  getAPIKeys(params = {}) {
    const queryParams = new URLSearchParams(params).toString();
    return get(`/api/v1/api-keys/keys/${queryParams ? '?' + queryParams : ''}`);
  },
  getAPIKey(id) {
    return get(`/api/v1/api-keys/keys/${id}/`);
  },
  createAPIKey(payload) {
    return post('/api/v1/api-keys/keys/', payload);
  },
  updateAPIKey(id, payload) {
    return put(`/api/v1/api-keys/keys/${id}/`, payload);
  },
  deleteAPIKey(id) {
    return del(`/api/v1/api-keys/keys/${id}/`);
  },
  getAnalyticsLogs(params = {}) {
    const queryParams = new URLSearchParams(params).toString();
    return get(`/api/v1/api-keys/logs/${queryParams ? '?' + queryParams : ''}`);
  }
};

export default {
  regionsAPI,
  alertsAPI,
  reportsAPI,
  organizationsAPI,
  satelliteProcessingAPI,
  analyticsAPI,
  geospatialAPI,
  dashboardAPI,
  usersAPI,
  mlModelsAPI,
  apiKeysAPI,
};


