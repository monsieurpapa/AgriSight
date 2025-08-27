# AgriSight
AgriSight uses satellite imagery to provide findings on crop health and land use, helping humanitarian organizations and local cooperatives make informed decisions to address food insecurity in conflict-affected regions.

The preliminary focus is to provide insights based of DRC's North Kivu and South Kivu provinces using geospatial data and API by Google Earth Engine, and EU's SentilHub (Which exposes satellite images data fron Sentinel 1 and 2 Satellites).

The google earth engine code so farm it accessible via this Google collab notebook : https://colab.research.google.com/drive/1JNhpqK8AP7oi6sYQ0-Kq2VX6MEiwqXf8?usp=sharing.
Alternatively, the code of this same notebook can be seen in the googlearthengine folder.

On the other hand, SentinelHub was also explored, and the details can be found in the sentinelhub folder, alongside its README file and all authentification details.

More details to follow


# AgriSight - Satellite-based Agricultural Monitoring Platform

AgriSight is a comprehensive B2B platform that leverages satellite data and advanced analytics to provide real-time agricultural monitoring and insights for humanitarian organizations, cooperatives, and government agencies operating in conflict-affected areas, particularly in the Democratic Republic of Congo (DRC).

## Features

### Core Capabilities
- **Multi-resolution Satellite Data Processing**: Utilizes Sentinel-2 satellite imagery for comprehensive crop health and land use monitoring
- **Advanced Vegetation Indices**: Calculates NDVI, EVI, NDWI, and SAVI for near real-time crop health assessment
- **Anomaly Detection**: Compares current imagery with historical baselines to identify agricultural decline or land abandonment
- **Multi-tenancy Support**: Organization-based access control with subscription plans and region-specific permissions
- **Geospatial Analysis**: Full GeoDjango integration for spatial data handling and analysis

### Platform Architecture
- **Microservices Architecture**: Docker-based containerized services for scalability and maintainability
- **Django Backend**: RESTful API with comprehensive data models and business logic
- **PostgreSQL with PostGIS**: Spatial database for geospatial data storage and queries
- **Celery Workers**: Asynchronous task processing for satellite data ingestion and analysis
- **Redis**: Message broker and caching layer
- **Nginx + HAProxy**: Load balancing and reverse proxy configuration
- **React Frontend**: Modern web interface for data visualization and management

## Project Structure

```
agrisight/
├── backend/                    # Django backend application
│   ├── agrisight/             # Django project settings
│   ├── apps/                  # Django applications
│   │   ├── users/             # User management
│   │   ├── organizations/     # Organization and subscription management
│   │   ├── geospatial/        # Spatial data models (regions, satellite images, etc.)
│   │   ├── analytics/         # Stress events and conflict data
│   │   ├── reports_alerts/    # Reports and alert system
│   │   └── api_keys_logs/     # API keys and usage analytics
│   ├── Dockerfile
│   └── requirements.txt
├── celery_worker/             # Celery worker for background tasks
├── celery_beat/               # Celery beat for scheduled tasks
├── frontend/                  # React frontend application
├── nginx/                     # Nginx configuration
├── haproxy/                   # HAProxy configuration
├── docker-compose.yml         # Service orchestration
└── .env                       # Environment variables
```

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd agrisight
   ```

2. **Environment Setup**
   ```bash
   cp .env.example .env
   # Edit .env file with your configuration
   ```

3. **Build and Start Services**
   ```bash
   docker-compose up --build
   ```

4. **Initialize Database**
   ```bash
   docker-compose exec backend python manage.py migrate
   docker-compose exec backend python manage.py createsuperuser
   ```

5. **Access the Platform**
   - Frontend: http://localhost
   - API Documentation: http://localhost/api/docs/
   - Admin Interface: http://localhost/admin/
   - HAProxy Stats: http://localhost:8404/stats

## API Documentation

The platform provides a comprehensive RESTful API with the following main endpoints:

### Authentication & Users
- `GET/POST /api/v1/users/` - User management
- `GET /api/v1/users/me/` - Current user information

### Organizations & Subscriptions
- `GET/POST /api/v1/organizations/` - Organization management
- `GET /api/v1/organizations/subscription-plans/` - Available subscription plans

### Geospatial Data
- `GET/POST /api/v1/geospatial/regions/` - Geographic regions
- `GET/POST /api/v1/geospatial/satellite-images/` - Satellite imagery metadata
- `GET/POST /api/v1/geospatial/vegetation-indices/` - Calculated vegetation indices
- `GET/POST /api/v1/geospatial/crops/` - Crop information
- `GET/POST /api/v1/geospatial/crop-mappings/` - Crop mapping data

### Analytics
- `GET/POST /api/v1/analytics/stress-events/` - Agricultural stress events
- `GET/POST /api/v1/analytics/conflict-events/` - Conflict event data
- `GET /api/v1/analytics/stress-events/summary/` - Stress event statistics

### Reports & Alerts
- `GET/POST /api/v1/reports-alerts/reports/` - Generated reports
- `GET/POST /api/v1/reports-alerts/alerts/` - System alerts
- `POST /api/v1/reports-alerts/alerts/{id}/mark-read/` - Mark alert as read

### API Keys & Analytics
- `GET/POST /api/v1/api-keys/` - API key management
- `GET /api/v1/api-keys/logs/` - Usage analytics
- `GET /api/v1/api-keys/usage-stats/` - Usage statistics

## Data Models

### Core Models

#### User & Organization Management
- **User**: Extended Django user model with organization association
- **Organization**: B2B client organizations with subscription plans
- **SubscriptionPlan**: Different service tiers with feature limitations

#### Geospatial Data
- **Region**: Geographic areas with PostGIS geometry fields
- **RegionAccess**: Organization-specific region access permissions
- **SatelliteImage**: Satellite imagery metadata and processing status
- **VegetationIndex**: Calculated indices (NDVI, EVI, NDWI, SAVI)
- **Crop**: Crop type information and characteristics
- **CropMapping**: Spatial crop distribution data

#### Analytics & Events
- **AgriculturalStressEvent**: Detected stress events with severity levels
- **ConflictEvent**: Conflict data that may impact agriculture

#### Reporting & Alerts
- **Report**: Generated reports for organizations
- **Alert**: Automated system alerts and notifications

#### System Management
- **APIKey**: Programmatic access keys for B2B clients
- **AnalyticsLog**: Usage tracking and billing data

## Satellite Data Processing

### Vegetation Indices
The platform calculates four key vegetation indices:

1. **NDVI (Normalized Difference Vegetation Index)**
   - Range: -1 to 1
   - Indicates vegetation health and density

2. **EVI (Enhanced Vegetation Index)**
   - Improved sensitivity in high biomass regions
   - Reduces atmospheric and soil background effects

3. **NDWI (Normalized Difference Water Index)**
   - Range: -1 to 1
   - Indicates water stress and moisture content

4. **SAVI (Soil Adjusted Vegetation Index)**
   - Minimizes soil brightness influences
   - Better for sparse vegetation areas

### Anomaly Detection
The system employs statistical analysis to detect anomalies:
- Compares current indices with historical baselines
- Uses standard deviation thresholds for anomaly identification
- Generates automated alerts for significant deviations
- Creates stress events with severity classifications (1-5 scale)

## Multi-tenancy & Access Control

### Organization-based Tenancy
- Each organization operates as an isolated tenant
- Subscription plans control feature access and limits
- Region-specific access permissions ensure data security

### Access Levels
- **View Only**: Read access to data and visualizations
- **Analysis Access**: Ability to run analytics and generate reports
- **Full Access**: Complete data management and configuration

## Development

### Backend Development
```bash
# Install dependencies
cd backend
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

### Frontend Development
```bash
# Install dependencies
cd frontend
npm install

# Start development server
npm start
```

### Running Tests
```bash
# Backend tests
docker-compose exec backend python manage.py test

# Frontend tests
docker-compose exec frontend npm test
```

## Deployment

### Production Deployment
1. Update environment variables for production
2. Set `DEBUG=False` in Django settings
3. Configure proper SSL certificates
4. Set up monitoring and logging
5. Configure backup strategies for PostgreSQL

### Scaling Considerations
- Celery workers can be scaled horizontally
- Database read replicas for improved performance
- CDN integration for static file delivery
- Load balancer configuration for high availability

## Security

### API Security
- Token-based authentication
- API key management for programmatic access
- Rate limiting and request throttling
- Input validation and sanitization

### Data Security
- Encrypted database connections
- Secure API key storage (hashed)
- Organization-based data isolation
- Audit logging for all operations

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For technical support or questions about the AgriSight platform, please contact:
- Email: support@agrisight.com
- Documentation: https://docs.agrisight.com
- Issue Tracker: https://github.com/agrisight/agrisight/issues

## Acknowledgments

- Sentinel-2 satellite data provided by the European Space Agency (ESA)
- PostGIS for spatial database capabilities
- Django and Django REST Framework for backend development
- React and Leaflet for frontend mapping capabilities


