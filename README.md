# AgriSight
AgriSight uses satellite imagery to provide findings on crop health and land use, helping humanitarian organizations and local cooperatives make informed decisions to address food insecurity in conflict-affected regions.

The preliminary focus is to provide insights based of DRC's North Kivu and South Kivu provinces using geospatial data and API by Google Earth Engine, and EU's SentilHub (Which exposes satellite images data fron Sentinel 1 and 2 Satellites).

The google earth engine code so farm it accessible via this Google collab notebook : https://colab.research.google.com/drive/1JNhpqK8AP7oi6sYQ0-Kq2VX6MEiwqXf8?usp=sharing.
Alternatively, the code of this same notebook can be seen in the googlearthengine folder.

On the other hand, SentinelHub was also explored, and the details can be found in the sentinelhub folder, alongside its README file and all authentification details.

More details to follow


# AgriSight 🌱

AgriSight is a comprehensive agricultural monitoring and analysis platform that leverages satellite imagery and geospatial data to provide actionable insights for agricultural management. The platform is built with a modern microservices architecture using Django, React, and various geospatial technologies.

## 🌟 Features

- **Satellite Data Integration**: Real-time and historical satellite imagery processing
- **Crop Health Monitoring**: NDVI and other vegetation indices analysis
- **Field Boundary Detection**: Automated field boundary identification
- **Anomaly Detection**: Machine learning models for detecting agricultural anomalies
- **Session-Based Authentication**: Secure session-based authentication system with CSRF protection
- **Interactive Maps**: Visualize and interact with geospatial data
- **Task Queueing**: Asynchronous task processing with Celery and Redis
- **Public Landing Page**: Marketing landing page with CTAs and product showcase
- **Public Demo**: Read-only demo with sample NDVI charts and map previews
- **User Profile Management**: Complete user profile editing and password management
- **Protected Routes**: Secure route protection with automatic redirects

## 🏗️ Tech Stack

### Backend
- **Django 4.2** - Python web framework
- **Django REST Framework** - Building RESTful APIs
- **PostgreSQL with PostGIS** - Geospatial database
- **Celery** - Asynchronous task queue
- **Redis** - Message broker and cache
- **GDAL/GEOS** - Geospatial data processing
- **Sentinel Hub** - Satellite imagery processing
- **django-allauth** - Authentication and account management
- **dj-rest-auth** - REST API authentication endpoints
- **Session Authentication** - Secure session-based authentication

### Frontend
- **React 18** - Frontend library
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Utility-first CSS framework
- **Radix UI** - Accessible UI components
- **React Query** - Data fetching and state management
- **Leaflet** - Interactive maps
- **Framer Motion** - Animation library
- **React Router** - Client-side routing
- **Axios** - HTTP client with CSRF support
- **Recharts** - Data visualization for charts

#### Public landing and demo

- Visit `/landing` for the marketing landing page with CTAs to register and view the public demo.
- Visit `/demo` for a read-only demo with a sample NDVI chart and a map preview. Demo data is static and loaded from `frontend/public/demo/`.
- Unauthenticated users navigating to protected routes are redirected to `/landing`.

#### Authentication system

- **Session-based authentication** with CSRF protection
- **User registration** with email verification (configurable)
- **Login/logout** functionality with secure session management
- **User profile management** with editable personal information
- **Password change** functionality
- **Protected routes** with automatic redirects for unauthenticated users
- **Public routes** for landing page, demo, and authentication pages

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.10+
- Node.js 18+
- pnpm (recommended) or npm

### Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/AgriSight.git
   cd AgriSight/agrisight
   ```

2. **Set up environment variables**
   Create a `.env` file in the `backend` directory with the following variables:
   ```
   DEBUG=True
   SECRET_KEY=your-secret-key
   DB_NAME=agrisight
   DB_USER=agrisight_user
   DB_PASSWORD=agrisight_password
   DB_HOST=postgres
   CELERY_BROKER_URL=redis://redis:6379/0
   SENTINEL_HUB_CLIENT_ID=your-client-id
   SENTINEL_HUB_CLIENT_SECRET=your-client-secret
   ```
   
   The frontend automatically uses `http://localhost:8000` as the API base URL in development.

3. **Start the application**
   ```bash
   docker-compose up --build
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Landing Page: http://localhost:3000/landing
   - Public Demo: http://localhost:3000/demo
   - Backend API: http://localhost:8000
   - Django Admin: http://localhost:8000/admin
   - Flower (Celery monitoring): http://localhost:5555

5. **Create your first user account**
   - Visit http://localhost:3000/register to create a new account
   - Or visit http://localhost:3000/login to sign in
   - Access the dashboard at http://localhost:3000/ after authentication

## 🧪 Running Tests

```bash
# Run backend tests
docker-compose exec backend python manage.py test

# Run frontend tests
cd frontend
pnpm test
```

## 🛠️ Project Structure

```
agrisight/
├── backend/               # Django backend
│   ├── agrisight/         # Project settings
│   ├── apps/              # Django apps
│   │   ├── authentication/ # Authentication and user management
│   │   ├── api/           # API endpoints
│   │   ├── fields/        # Field management
│   │   ├── satellite/     # Satellite data processing
│   │   └── users/         # User management
│   └── manage.py          # Django management script
│
├── celery_beat/          # Celery beat scheduler
├── celery_worker/        # Celery worker configuration
├── frontend/             # React frontend
│   ├── public/           # Static files
│   │   └── demo/         # Demo data (NDVI charts, map previews)
│   └── src/              # Source code
│       ├── components/   # Reusable components
│       │   └── ui/       # UI component library
│       ├── contexts/     # React contexts (AuthContext)
│       ├── hooks/        # Custom hooks
│       ├── lib/          # Utility libraries (API, auth, utils)
│       ├── pages/        # Page components
│       └── utils/        # Utility functions
│
├── data/                 # Data storage
├── docs/                 # Documentation
└── docker-compose.yml    # Docker Compose configuration
```

## 🔧 Environment Configuration

- **Development**: Set `DEBUG=True` for detailed error pages and auto-reload
- **Production**: Set `DEBUG=False` and configure proper security settings
- **Testing**: Uses a separate test database

### Authentication Configuration

- **Session-based authentication** with CSRF protection enabled
- **Email verification** can be disabled for development (`ACCOUNT_EMAIL_VERIFICATION = 'none'`)
- **CORS settings** configured for development with credentials support
- **CSRF tokens** automatically handled by frontend interceptors

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📚 Documentation

For detailed documentation, please see:
- [API Documentation](http://localhost:8000/api/docs/)
- [Deployment Guide](DEPLOYMENT_GUIDE.md)
- [Setup Guide](SETUP_GUIDE.md)
- [Frontend Implementation](FRONTEND_IMPLEMENTATION.md)
- [Authentication Architecture](AUTHENTICATION_ARCHITECTURE.md)
- [Sentinel Hub Integration](SENTINEL_HUB_INTEGRATION.md)

## 🔐 Security Features

- **CSRF Protection**: All state-changing requests protected with CSRF tokens
- **Session Security**: HTTP-only cookies with secure session management
- **CORS Configuration**: Properly configured for development and production
- **Input Validation**: Server-side validation for all user inputs
- **Authentication**: Secure session-based authentication system

## 🚀 Recent Updates

### Authentication System Overhaul
- Migrated from JWT to session-based authentication for better security
- Implemented CSRF protection for all API requests
- Added comprehensive user profile management
- Created public landing page and demo functionality

### Frontend Enhancements
- Added public landing page with marketing content
- Implemented public demo with sample NDVI charts
- Created user profile management interface
- Enhanced route protection and navigation

### Backend Improvements
- Simplified authentication flow with session management
- Added CSRF token endpoint for frontend integration
- Improved error handling and logging
- Enhanced API documentation and testing

## 📬 Contact

For questions or support, please open an issue or contact the maintainers.

---

<div align="center">
  Made with ❤️ by the AgriSight Team
</div>
