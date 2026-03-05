# 🛰️ AgriSight

### Satellite-Driven Agricultural Intelligence Platform

[![CI](https://github.com/monsieurpapa/AgriSight/actions/workflows/ci.yml/badge.svg)](https://github.com/monsieurpapa/AgriSight/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/release/python-3110/)
[![React 19](https://img.shields.io/badge/react-19-61dafb.svg)](https://reactjs.org/)

AgriSight is a comprehensive B2B monitoring platform that leverages Sentinel-2 satellite imagery and geospatial analytics to provide real-time insights into crop health, vegetation stress, and land utilization. Designed for humanitarian organizations, agricultural cooperatives, and government agencies.

---

## 🚀 Key Features

- **🛰️ Satellite Monitoring**: Automated Sentinel-2 data ingestion and processing (NDVI, EVI, NDWI).
- **🗺️ Geospatial Analytics**: PostGIS-powered region monitoring and spatial analysis.
- **🚨 Intelligent Alerting**: Real-time anomaly detection and multi-channel alerting system.
- **📊 Executive Dashboards**: High-level visual summaries and detailed geospatial reports.
- **🛡️ Enterprise Grade**: RBAC, audit trails, and soft-delete capabilities.
- **📱 PWA & Offline Support**: Resilient monitoring even in remote areas with limited connectivity.

## 🛠️ Tech Stack

- **Frontend**: React 19, Vite, Tailwind CSS, Radix UI, Leaflet.
- **Backend**: Django 5.1, Django REST Framework, PostGIS.
- **Task Queue**: Celery, Redis.
- **Observability**: Flower, Sentry (ready).
- **Deployment**: Docker, Docker Compose, Nginx, HAProxy.

## 📖 Documentation Index

- [**Architecture Overview**](docs/ARCHITECTURE.md) - System design and workflow diagrams.
- [**Deployment Guide**](docs/DEPLOYMENT.md) - Production setup and CI/CD details.
- [**Operational Manual**](docs/OPERATIONS.md) - Backups, monitoring, and scaling.
- [**API Documentation**](docs/API_GUIDE.md) - Consuming the AgriSight REST API.
- [**Contributing Guide**](CONTRIBUTING.md) - Local development and PR guidelines.

## 🚦 Quick Start

### Prerequisites
- Docker & Docker Compose
- Sentinel Hub API Credentials

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/monsieurpapa/AgriSight.git
   cd AgriSight
   ```

2. **Configure environment**:
   ```bash
   cp agrisight/backend/.env.example agrisight/backend/.env
   # Edit agrisight/backend/.env with your credentials
   ```

3. **Spin up the stack**:
   ```bash
   docker-compose up --build
   ```

4. **Access the application**:
   - Frontend: [http://localhost](http://localhost)
   - Backend API: [http://localhost/api/v1/](http://localhost/api/v1/)
   - Flower (Monitoring): [http://localhost:5555](http://localhost:5555)

## 🛡️ Security & Integrity

AgriSight follows industry best practices:
- **JWT-in-Cookies**: Secure authentication handshake.
- **Audit Trails**: Complete history tracking for critical entities.
- **Soft Deletes**: Preventing accidental data loss.

---

© 2026 AgriSight Team. All rights reserved.
