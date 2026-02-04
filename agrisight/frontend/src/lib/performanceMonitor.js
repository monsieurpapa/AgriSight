/**
 * Performance Monitoring Utilities
 * 
 * Track and monitor frontend performance metrics
 */

class PerformanceMonitor {
  constructor() {
    this.metrics = [];
    this.thresholds = {
      pageLoad: 3000,      // 3 seconds
      componentRender: 500, // 500ms
      apiCall: 2000,       // 2 seconds
    };
  }

  /**
   * Measure component render time
   */
  measureRender(componentName, fn) {
    const start = performance.now();
    const result = fn();
    const duration = performance.now() - start;

    this.recordMetric('render', componentName, duration);

    if (duration > this.thresholds.componentRender) {
      console.warn(
        `⚠️  Slow component render: ${componentName} took ${duration.toFixed(2)}ms`
      );
    }

    return result;
  }

  /**
   * Measure API call duration
   */
  measureApiCall(endpoint, fn) {
    const start = performance.now();
    return Promise.resolve(fn()).then((result) => {
      const duration = performance.now() - start;
      this.recordMetric('api', endpoint, duration);

      if (duration > this.thresholds.apiCall) {
        console.warn(
          `⚠️  Slow API call: ${endpoint} took ${duration.toFixed(2)}ms`
        );
      }

      return result;
    });
  }

  /**
   * Record performance metric
   */
  recordMetric(type, name, duration) {
    const metric = {
      type,
      name,
      duration,
      timestamp: new Date().toISOString(),
    };

    this.metrics.push(metric);

    // Keep only last 100 metrics
    if (this.metrics.length > 100) {
      this.metrics.shift();
    }
  }

  /**
   * Get page load time
   */
  getPageLoadTime() {
    if (!window.performance) return null;

    const perfData = performance.getEntriesByType('navigation')[0];
    if (!perfData) return null;

    return {
      domInteractive: perfData.domInteractive,
      domComplete: perfData.domComplete,
      loadEventEnd: perfData.loadEventEnd,
      totalLoadTime: perfData.loadEventEnd - perfData.navigationStart,
    };
  }

  /**
   * Get resource timings
   */
  getResourceTimings() {
    if (!window.performance) return [];

    return performance.getEntriesByType('resource').map((resource) => ({
      name: resource.name,
      duration: resource.duration,
      size: resource.transferSize || 0,
    }));
  }

  /**
   * Get metrics summary
   */
  getSummary() {
    const summary = {
      totalMetrics: this.metrics.length,
      byType: {},
      slowestComponents: [],
      slowestApis: [],
      pageLoad: this.getPageLoadTime(),
    };

    // Group by type
    this.metrics.forEach((metric) => {
      if (!summary.byType[metric.type]) {
        summary.byType[metric.type] = [];
      }
      summary.byType[metric.type].push(metric);
    });

    // Find slowest components
    const renderMetrics = summary.byType.render || [];
    summary.slowestComponents = renderMetrics
      .sort((a, b) => b.duration - a.duration)
      .slice(0, 5);

    // Find slowest APIs
    const apiMetrics = summary.byType.api || [];
    summary.slowestApis = apiMetrics
      .sort((a, b) => b.duration - a.duration)
      .slice(0, 5);

    return summary;
  }

  /**
   * Log performance report
   */
  logReport() {
    const summary = this.getSummary();

    console.group('📊 Performance Report');

    // Page load
    if (summary.pageLoad) {
      console.group('Page Load');
      console.log(`Total: ${summary.pageLoad.totalLoadTime.toFixed(2)}ms`);
      console.log(`DOM Interactive: ${summary.pageLoad.domInteractive.toFixed(2)}ms`);
      console.log(`DOM Complete: ${summary.pageLoad.domComplete.toFixed(2)}ms`);
      console.groupEnd();
    }

    // Slowest components
    if (summary.slowestComponents.length > 0) {
      console.group('Slowest Components');
      summary.slowestComponents.forEach((metric) => {
        console.log(`${metric.name}: ${metric.duration.toFixed(2)}ms`);
      });
      console.groupEnd();
    }

    // Slowest APIs
    if (summary.slowestApis.length > 0) {
      console.group('Slowest APIs');
      summary.slowestApis.forEach((metric) => {
        console.log(`${metric.name}: ${metric.duration.toFixed(2)}ms`);
      });
      console.groupEnd();
    }

    // Resources
    const resources = this.getResourceTimings();
    if (resources.length > 0) {
      const totalSize = resources.reduce((sum, r) => sum + r.size, 0);
      console.group('Resources');
      console.log(`Total resources: ${resources.length}`);
      console.log(`Total size: ${(totalSize / 1024 / 1024).toFixed(2)}MB`);
      console.groupEnd();
    }

    console.groupEnd();
  }

  /**
   * Export metrics for analysis
   */
  exportMetrics() {
    const summary = this.getSummary();
    const dataStr = JSON.stringify(summary, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `performance-metrics-${Date.now()}.json`;
    link.click();
    URL.revokeObjectURL(url);
  }

  /**
   * Clear all metrics
   */
  clear() {
    this.metrics = [];
  }

  /**
   * Set performance threshold
   */
  setThreshold(type, milliseconds) {
    this.thresholds[type] = milliseconds;
  }
}

// Create singleton instance
const performanceMonitor = new PerformanceMonitor();

// Expose in development
if (import.meta.env.DEV) {
  window.performanceMonitor = performanceMonitor;
}

export default performanceMonitor;

/**
 * React Hook for measuring component render time
 */
export const useRenderTime = (componentName) => {
  const startTimeRef = React.useRef(performance.now());

  React.useEffect(() => {
    const duration = performance.now() - startTimeRef.current;
    performanceMonitor.recordMetric('render', componentName, duration);

    if (import.meta.env.DEV) {
      console.log(
        `⏱️  ${componentName} rendered in ${duration.toFixed(2)}ms`
      );
    }
  }, [componentName]);
};

/**
 * React Hook for measuring component lifecycle
 */
export const usePerformanceMetric = (metricName) => {
  const startTimeRef = React.useRef(null);

  const start = React.useCallback(() => {
    startTimeRef.current = performance.now();
  }, []);

  const end = React.useCallback(() => {
    if (startTimeRef.current) {
      const duration = performance.now() - startTimeRef.current;
      performanceMonitor.recordMetric('custom', metricName, duration);
      startTimeRef.current = null;
    }
  }, [metricName]);

  return { start, end };
};

/**
 * Monitor Web Vitals
 */
export const initWebVitals = () => {
  // Largest Contentful Paint (LCP)
  if ('PerformanceObserver' in window) {
    try {
      const observer = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        const lastEntry = entries[entries.length - 1];
        performanceMonitor.recordMetric('metric', 'LCP', lastEntry.renderTime || lastEntry.loadTime);
      });
      observer.observe({ entryTypes: ['largest-contentful-paint'] });
    } catch (e) {
      console.warn('Could not observe LCP');
    }

    // First Input Delay (FID) / Interaction to Next Paint (INP)
    try {
      const observer = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          performanceMonitor.recordMetric('metric', 'INP', entry.processingDuration);
        }
      });
      observer.observe({ entryTypes: ['first-input', 'event'] });
    } catch (e) {
      console.warn('Could not observe FID/INP');
    }

    // Cumulative Layout Shift (CLS)
    try {
      const observer = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          performanceMonitor.recordMetric('metric', 'CLS', entry.value);
        }
      });
      observer.observe({ entryTypes: ['layout-shift'] });
    } catch (e) {
      console.warn('Could not observe CLS');
    }
  }
};
