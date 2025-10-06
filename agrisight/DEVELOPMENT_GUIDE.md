# AgriSight Development Guide

## Overview

This guide provides comprehensive instructions for setting up, developing, and contributing to the AgriSight platform. It covers everything from initial setup to advanced development practices.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Development Setup](#development-setup)
3. [Project Structure](#project-structure)
4. [Development Workflow](#development-workflow)
5. [Code Standards](#code-standards)
6. [Testing](#testing)
7. [Debugging](#debugging)
8. [Performance Optimization](#performance-optimization)
9. [Contributing](#contributing)
10. [Troubleshooting](#troubleshooting)

## Prerequisites

### Required Software

- **Docker & Docker Compose**: Latest version
- **Python**: 3.10+ (for local development)
- **Node.js**: 18+ (for frontend development)
- **pnpm**: Latest version (recommended package manager)
- **Git**: Latest version
- **VS Code**: Recommended IDE with extensions

### Recommended VS Code Extensions

```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.pylint",
    "ms-python.black-formatter",
    "bradlc.vscode-tailwindcss",
    "esbenp.prettier-vscode",
    "ms-vscode.vscode-typescript-next",
    "ms-vscode.vscode-json",
    "redhat.vscode-yaml",
    "ms-vscode-remote.remote-containers"
  ]
}
```

## Development Setup

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/AgriSight.git
cd AgriSight/agrisight
```

### 2. Environment Configuration

Create environment files for different environments:

#### Backend Environment (`.env`)
```bash
# Database
DEBUG=True
SECRET_KEY=your-development-secret-key
DB_NAME=agrisight_dev
DB_USER=agrisight_user
DB_PASSWORD=agrisight_password
DB_HOST=postgres
DB_PORT=5432

# Redis
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# Sentinel Hub (Optional for development)
SENTINEL_HUB_CLIENT_ID=your-client-id
SENTINEL_HUB_CLIENT_SECRET=your-client-secret

# Email (Development)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

# Security (Development)
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

#### Frontend Environment (`.env.local`)
```bash
VITE_API_BASE_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000/ws/
VITE_APP_NAME=AgriSight
VITE_APP_VERSION=1.0.0
```

### 3. Start Development Environment

```bash
# Start all services
docker-compose up --build -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### 4. Initial Setup

```bash
# Create superuser
docker-compose exec backend python manage.py createsuperuser

# Run migrations
docker-compose exec backend python manage.py migrate

# Collect static files
docker-compose exec backend python manage.py collectstatic --noinput

# Load sample data (optional)
docker-compose exec backend python manage.py loaddata sample_data.json
```

### 5. Access Development Environment

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Django Admin**: http://localhost:8000/admin
- **API Documentation**: http://localhost:8000/api/docs/
- **Flower (Celery)**: http://localhost:5555

## Project Structure

```
agrisight/
├── backend/                    # Django backend
│   ├── agrisight/             # Project settings
│   │   ├── settings/          # Environment-specific settings
│   │   ├── urls.py            # URL configuration
│   │   └── wsgi.py            # WSGI configuration
│   ├── apps/                  # Django applications
│   │   ├── authentication/    # User authentication
│   │   ├── core/              # Core utilities and middleware
│   │   ├── geospatial/        # Geospatial data management
│   │   ├── analytics/         # Analytics and reporting
│   │   ├── satellite_processing/ # Satellite data processing
│   │   ├── ml_models/         # Machine learning models
│   │   ├── reports_alerts/    # Reports and alerts
│   │   ├── organizations/     # Organization management
│   │   ├── users/             # User management
│   │   └── api_keys_logs/     # API key management
│   ├── manage.py              # Django management script
│   ├── requirements.txt       # Python dependencies
│   └── Dockerfile             # Backend container
│
├── frontend/                   # React frontend
│   ├── public/                # Static files
│   │   └── demo/              # Demo data
│   ├── src/                   # Source code
│   │   ├── components/        # Reusable components
│   │   │   └── ui/            # UI component library
│   │   ├── contexts/          # React contexts
│   │   ├── hooks/             # Custom hooks
│   │   ├── lib/               # Utility libraries
│   │   ├── pages/             # Page components
│   │   └── utils/             # Utility functions
│   ├── package.json           # Node.js dependencies
│   ├── vite.config.js         # Vite configuration
│   └── Dockerfile             # Frontend container
│
├── celery_beat/               # Celery beat scheduler
├── celery_worker/             # Celery worker configuration
├── data/                      # Data storage
├── docs/                      # Documentation
├── docker-compose.yml         # Docker Compose configuration
├── .gitignore                 # Git ignore rules
└── README.md                  # Project documentation
```

## Development Workflow

### 1. Feature Development

```bash
# Create feature branch
git checkout -b feature/new-feature

# Make changes
# ... develop feature ...

# Run tests
docker-compose exec backend python manage.py test
cd frontend && pnpm test

# Commit changes
git add .
git commit -m "feat: add new feature"

# Push and create PR
git push origin feature/new-feature
```

### 2. Database Migrations

```bash
# Create migration
docker-compose exec backend python manage.py makemigrations

# Apply migration
docker-compose exec backend python manage.py migrate

# Check migration status
docker-compose exec backend python manage.py showmigrations
```

### 3. Frontend Development

```bash
# Install dependencies
cd frontend
pnpm install

# Start development server
pnpm dev

# Build for production
pnpm build

# Run tests
pnpm test

# Lint code
pnpm lint

# Format code
pnpm format
```

### 4. Backend Development

```bash
# Install dependencies (if running locally)
pip install -r requirements.txt

# Run development server
python manage.py runserver

# Run tests
python manage.py test

# Check code quality
pylint apps/
black apps/
isort apps/
```

## Code Standards

### Python/Django Standards

#### Code Style
```python
# Use Black for formatting
black apps/

# Use isort for import sorting
isort apps/

# Use pylint for linting
pylint apps/
```

#### Django Best Practices
```python
# Model naming
class AgriculturalStressEvent(models.Model):
    """Model for agricultural stress events."""
    
    class Meta:
        verbose_name = "Agricultural Stress Event"
        verbose_name_plural = "Agricultural Stress Events"
        ordering = ['-detection_date']

# View naming
class StressEventListCreateView(generics.ListCreateAPIView):
    """List and create stress events."""
    
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = StressEventSerializer
    
    def get_queryset(self):
        """Return filtered queryset based on user permissions."""
        user = self.request.user
        if user.user_type == 'admin':
            return AgriculturalStressEvent.objects.all()
        return AgriculturalStressEvent.objects.filter(
            region__organizations=user.organization
        )

# Serializer naming
class StressEventSerializer(serializers.ModelSerializer):
    """Serializer for stress events."""
    
    class Meta:
        model = AgriculturalStressEvent
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']
```

### React/JavaScript Standards

#### Code Style
```javascript
// Use Prettier for formatting
prettier --write src/

// Use ESLint for linting
eslint src/

// Use TypeScript for type safety
// (when implemented)
```

#### React Best Practices
```jsx
// Component structure
import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { useAuth } from '../contexts/AuthContext';
import { api } from '../lib/api';

const Dashboard = () => {
  const { user } = useAuth();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const response = await api.getDashboardData();
        setData(response);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Dashboard</CardTitle>
        </CardHeader>
        <CardContent>
          {/* Dashboard content */}
        </CardContent>
      </Card>
    </div>
  );
};

export default Dashboard;
```

### Git Standards

#### Commit Message Format
```
type(scope): description

feat(auth): add password reset functionality
fix(api): resolve CORS issue with frontend
docs(readme): update installation instructions
style(frontend): format code with prettier
refactor(backend): extract common utilities
test(api): add integration tests for auth endpoints
chore(deps): update dependencies
```

#### Branch Naming
```
feature/user-authentication
bugfix/cors-issue
hotfix/security-patch
docs/api-documentation
refactor/database-models
```

## Testing

### Backend Testing

#### Unit Tests
```python
# tests.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.analytics.models import AgriculturalStressEvent

User = get_user_model()

class StressEventModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_stress_event_creation(self):
        """Test stress event creation."""
        event = AgriculturalStressEvent.objects.create(
            stress_type='drought',
            severity='high',
            region=self.region,
            detected_by=self.user
        )
        self.assertEqual(event.stress_type, 'drought')
        self.assertEqual(event.severity, 'high')
```

#### API Tests
```python
# api_tests.py
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()

class StressEventAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_create_stress_event(self):
        """Test creating a stress event via API."""
        data = {
            'stress_type': 'drought',
            'severity': 'high',
            'region': self.region.id,
            'description': 'Severe drought conditions detected'
        }
        response = self.client.post('/api/v1/analytics/stress-events/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
```

#### Integration Tests
```python
# integration_tests.py
from django.test import TestCase
from apps.satellite_processing.tasks import process_region_satellite_data

class SatelliteProcessingIntegrationTest(TestCase):
    def test_end_to_end_processing(self):
        """Test complete satellite data processing workflow."""
        # Create test region
        region = Region.objects.create(
            name='Test Region',
            geometry=test_geometry
        )
        
        # Trigger processing
        task = process_region_satellite_data.delay(region.id)
        
        # Wait for completion
        result = task.get(timeout=30)
        
        # Verify results
        self.assertTrue(result['success'])
        self.assertGreater(len(result['vegetation_indices']), 0)
```

### Frontend Testing

#### Component Tests
```javascript
// Dashboard.test.jsx
import { render, screen } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import Dashboard from './Dashboard';

const createTestQueryClient = () => new QueryClient({
  defaultOptions: {
    queries: { retry: false },
    mutations: { retry: false },
  },
});

const TestWrapper = ({ children }) => {
  const queryClient = createTestQueryClient();
  return (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
};

describe('Dashboard', () => {
  it('renders dashboard title', () => {
    render(
      <TestWrapper>
        <Dashboard />
      </TestWrapper>
    );
    
    expect(screen.getByText('Welcome back')).toBeInTheDocument();
  });
});
```

#### API Integration Tests
```javascript
// api.test.js
import { api } from '../lib/api';

describe('API Integration', () => {
  it('fetches regions data', async () => {
    const regions = await api.regions.getRegions();
    expect(regions).toHaveProperty('results');
    expect(Array.isArray(regions.results)).toBe(true);
  });
});
```

### Running Tests

```bash
# Backend tests
docker-compose exec backend python manage.py test
docker-compose exec backend python manage.py test apps.analytics.tests.StressEventModelTest

# Frontend tests
cd frontend
pnpm test
pnpm test -- --coverage

# End-to-end tests
python test_new_features.py
```

## Debugging

### Backend Debugging

#### Django Debug Toolbar
```python
# settings.py
if DEBUG:
    INSTALLED_APPS += ['debug_toolbar']
    MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
    INTERNAL_IPS = ['127.0.0.1', 'localhost']
```

#### Logging Configuration
```python
# settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'logs/agrisight.log',
        },
    },
    'loggers': {
        'apps': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
```

#### Database Debugging
```python
# Debug queries
from django.db import connection
from django.test.utils import override_settings

@override_settings(DEBUG=True)
def debug_queries():
    # Your code here
    print(connection.queries)
```

### Frontend Debugging

#### React Developer Tools
- Install React Developer Tools browser extension
- Use React Query DevTools for API debugging

#### Console Debugging
```javascript
// API debugging
const api = {
  async getRegions() {
    console.log('Fetching regions...');
    try {
      const response = await fetch('/api/v1/geospatial/regions/');
      console.log('Response:', response);
      return response.json();
    } catch (error) {
      console.error('API Error:', error);
      throw error;
    }
  }
};
```

#### Network Debugging
```javascript
// Axios interceptors for debugging
axios.interceptors.request.use(request => {
  console.log('Request:', request);
  return request;
});

axios.interceptors.response.use(
  response => {
    console.log('Response:', response);
    return response;
  },
  error => {
    console.error('Error:', error);
    return Promise.reject(error);
  }
);
```

## Performance Optimization

### Backend Optimization

#### Database Optimization
```python
# Use select_related and prefetch_related
regions = Region.objects.select_related('geometry').prefetch_related('organizations')

# Database indexing
class StressEvent(models.Model):
    region = models.ForeignKey(Region, on_delete=models.CASCADE, db_index=True)
    detection_date = models.DateTimeField(db_index=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['region', 'detection_date']),
            models.Index(fields=['severity', 'detection_date']),
        ]
```

#### Caching
```python
# Redis caching
from django.core.cache import cache

def get_vegetation_data(region_id):
    cache_key = f'vegetation_data_{region_id}'
    data = cache.get(cache_key)
    
    if data is None:
        data = calculate_vegetation_data(region_id)
        cache.set(cache_key, data, 3600)  # Cache for 1 hour
    
    return data
```

### Frontend Optimization

#### Code Splitting
```javascript
// Lazy loading components
const MapView = lazy(() => import('./pages/MapView'));
const Analytics = lazy(() => import('./pages/Analytics'));

// Route-based code splitting
const routes = [
  {
    path: '/map',
    element: (
      <Suspense fallback={<div>Loading...</div>}>
        <MapView />
      </Suspense>
    ),
  },
];
```

#### Performance Monitoring
```javascript
// Performance monitoring
import { getCLS, getFID, getFCP, getLCP, getTTFB } from 'web-vitals';

function sendToAnalytics(metric) {
  console.log(metric);
  // Send to analytics service
}

getCLS(sendToAnalytics);
getFID(sendToAnalytics);
getFCP(sendToAnalytics);
getLCP(sendToAnalytics);
getTTFB(sendToAnalytics);
```

## Contributing

### 1. Fork and Clone
```bash
git clone https://github.com/yourusername/AgriSight.git
cd AgriSight
```

### 2. Create Feature Branch
```bash
git checkout -b feature/your-feature-name
```

### 3. Make Changes
- Follow code standards
- Write tests for new functionality
- Update documentation

### 4. Test Changes
```bash
# Backend tests
docker-compose exec backend python manage.py test

# Frontend tests
cd frontend && pnpm test

# Integration tests
python test_new_features.py
```

### 5. Submit Pull Request
- Provide clear description
- Reference related issues
- Include screenshots if UI changes
- Ensure CI passes

### Code Review Process
1. Automated tests must pass
2. Code review by maintainers
3. Security review for sensitive changes
4. Performance review for optimization changes

## Troubleshooting

### Common Issues

#### Docker Issues
```bash
# Clean up Docker
docker-compose down -v
docker system prune -a

# Rebuild containers
docker-compose up --build --force-recreate
```

#### Database Issues
```bash
# Reset database
docker-compose down -v
docker-compose up -d postgres
docker-compose exec backend python manage.py migrate
```

#### Frontend Issues
```bash
# Clear node modules
cd frontend
rm -rf node_modules
rm pnpm-lock.yaml
pnpm install
```

#### Permission Issues
```bash
# Fix file permissions
sudo chown -R $USER:$USER .
chmod -R 755 .
```

### Getting Help

1. **Check Documentation**: Review relevant documentation files
2. **Search Issues**: Look for similar issues in GitHub
3. **Create Issue**: Provide detailed information about the problem
4. **Join Community**: Participate in discussions and forums

### Development Resources

- **Django Documentation**: https://docs.djangoproject.com/
- **React Documentation**: https://react.dev/
- **Docker Documentation**: https://docs.docker.com/
- **PostGIS Documentation**: https://postgis.net/documentation/

---

*This development guide is regularly updated to reflect current best practices and project requirements.*
