# AgriSight 🌱

AgriSight is a comprehensive agricultural monitoring and analysis platform that leverages satellite imagery and geospatial data to provide actionable insights for agricultural management. The platform is built with a modern microservices architecture using Django, React, and various geospatial technologies.

## 🌟 Features

- **Satellite Data Integration**: Real-time and historical satellite imagery processing
- **Crop Health Monitoring**: NDVI and other vegetation indices analysis
- **Field Boundary Detection**: Automated field boundary identification
- **Anomaly Detection**: Machine learning models for detecting agricultural anomalies
- **User Authentication**: Secure JWT-based authentication system
- **Interactive Maps**: Visualize and interact with geospatial data
- **Task Queueing**: Asynchronous task processing with Celery and Redis

## 🏗️ Tech Stack

### Backend
- **Django 4.2** - Python web framework
- **Django REST Framework** - Building RESTful APIs
- **PostgreSQL with PostGIS** - Geospatial database
- **Celery** - Asynchronous task queue
- **Redis** - Message broker and cache
- **GDAL/GEOS** - Geospatial data processing
- **Sentinel Hub** - Satellite imagery processing

### Frontend
- **React 18** - Frontend library
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Utility-first CSS framework
- **Radix UI** - Accessible UI components
- **React Query** - Data fetching and state management
- **Leaflet** - Interactive maps
- **Framer Motion** - Animation library

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

3. **Start the application**
   ```bash
   docker-compose up --build
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - Django Admin: http://localhost:8000/admin
   - Flower (Celery monitoring): http://localhost:5555

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
│   └── src/              # Source code
│       ├── components/   # Reusable components
│       ├── contexts/     # React contexts
│       ├── hooks/        # Custom hooks
│       ├── pages/        # Page components
│       ├── services/     # API services
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

## 📬 Contact

For questions or support, please open an issue or contact the maintainers.

---

<div align="center">
  Made with ❤️ by the AgriSight Team
</div>
