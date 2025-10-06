# AgriSight Makefile Usage Guide

## Overview
The AgriSight platform includes a comprehensive Makefile that provides easy-to-use commands for all platform operations, maintenance, and development tasks.

## Quick Start

### Basic Operations
```bash
# Show all available commands
make help

# Start the platform
make up

# Stop the platform
make down

# Restart the platform
make restart

# View logs
make logs
```

## Command Categories

### 🐳 Docker Operations
| Command | Description |
|---------|-------------|
| `make build` | Build all Docker containers |
| `make build-no-cache` | Build containers without cache |
| `make up` | Start all services in detached mode |
| `make up-build` | Build and start all services |
| `make down` | Stop all services |
| `make restart` | Restart all services |
| `make restart-backend` | Restart only backend service |
| `make restart-frontend` | Restart only frontend service |
| `make restart-db` | Restart database service |

### 📊 Monitoring & Logs
| Command | Description |
|---------|-------------|
| `make logs` | Show logs for all services |
| `make logs-backend` | Show backend logs |
| `make logs-frontend` | Show frontend logs |
| `make logs-db` | Show database logs |
| `make logs-celery` | Show Celery worker logs |
| `make logs-redis` | Show Redis logs |
| `make status` | Show status of all containers |
| `make health-check` | Check health of all services |
| `make monitor` | Real-time monitoring dashboard |

### 🗄️ Database Operations
| Command | Description |
|---------|-------------|
| `make migrate` | Run Django database migrations |
| `make makemigrations` | Create new Django migrations |
| `make db-reset` | Reset database (⚠️ DANGEROUS) |
| `make backup-db` | Backup database |
| `make restore-db BACKUP_FILE=file.sql` | Restore database from backup |

### 🛠️ Django Management
| Command | Description |
|---------|-------------|
| `make collectstatic` | Collect static files |
| `make createsuperuser` | Create Django superuser |
| `make shell` | Open Django shell |
| `make dbshell` | Open database shell |
| `make check` | Run Django system checks |

### 🧪 Testing & Quality
| Command | Description |
|---------|-------------|
| `make test` | Run all tests |
| `make test-coverage` | Run tests with coverage |
| `make lint-backend` | Lint backend code |
| `make lint-frontend` | Lint frontend code |
| `make format-backend` | Format backend code |
| `make format-frontend` | Format frontend code |
| `make security-check` | Run security checks |

### ⚡ Celery Operations
| Command | Description |
|---------|-------------|
| `make celery-worker` | Start Celery worker |
| `make celery-beat` | Start Celery beat scheduler |
| `make celery-flower` | Start Celery Flower monitoring |
| `make celery-purge` | Purge all Celery tasks |

### 💾 Backup & Restore
| Command | Description |
|---------|-------------|
| `make backup-db` | Backup database |
| `make backup-media` | Backup media files |
| `make backup-all` | Backup database and media |
| `make restore-db BACKUP_FILE=file.sql` | Restore database |

### 🧹 Cleanup Operations
| Command | Description |
|---------|-------------|
| `make clean-docker` | Clean Docker system |
| `make clean-volumes` | Remove all volumes (⚠️ DANGEROUS) |
| `make clean-all` | Clean everything (⚠️ DANGEROUS) |

### 🚀 Production Operations
| Command | Description |
|---------|-------------|
| `make prod-build` | Build for production |
| `make prod-up` | Start production services |
| `make prod-down` | Stop production services |

### 🔧 Development Helpers
| Command | Description |
|---------|-------------|
| `make setup` | Initial setup for new environment |
| `make dev-shell` | Open development shell |
| `make dev-logs` | Follow development logs |
| `make dev-reset` | Reset development environment |
| `make debug-backend` | Debug backend service |
| `make debug-frontend` | Debug frontend service |

### ⚡ Quick Commands
| Command | Description |
|---------|-------------|
| `make quick-restart` | Quick restart (stop, build, start) |
| `make quick-logs` | Quick view of recent logs |
| `make quick-status` | Quick status check |

### 🚨 Emergency Commands
| Command | Description |
|---------|-------------|
| `make emergency-stop` | Emergency stop all services |
| `make emergency-restart` | Emergency restart all services |

## Common Workflows

### Initial Setup
```bash
# Clone the repository and navigate to agrisight folder
cd agrisight

# Initial setup
make setup

# Create superuser
make createsuperuser

# Start all services
make up
```

### Daily Development
```bash
# Start development environment
make up

# View logs
make logs

# Run tests
make test

# Check status
make status
```

### Code Changes
```bash
# After making changes to backend
make restart-backend

# After making changes to frontend
make restart-frontend

# After database model changes
make makemigrations
make migrate
```

### Maintenance
```bash
# Run maintenance tasks
make maintenance

# Backup data
make backup-all

# Update dependencies
make update-deps

# Security check
make security-check
```

### Production Deployment
```bash
# Build for production
make prod-build

# Start production services
make prod-up

# Monitor production
make monitor
```

## Environment Variables

The Makefile respects the following environment variables:

- `BACKUP_FILE`: Used with restore commands
- `DOCKER_COMPOSE_FILE`: Override default docker-compose file
- `DJANGO_SETTINGS_MODULE`: Override Django settings

## Troubleshooting

### Common Issues

1. **Services not starting**
   ```bash
   make logs
   make status
   ```

2. **Database connection issues**
   ```bash
   make restart-db
   make migrate
   ```

3. **Frontend not loading**
   ```bash
   make restart-frontend
   make collectstatic
   ```

4. **Permission issues**
   ```bash
   make clean-docker
   make up-build
   ```

### Getting Help

```bash
# Show all available commands
make help

# Check service health
make health-check

# View service status
make status
```

## Best Practices

1. **Always backup before major changes**
   ```bash
   make backup-all
   ```

2. **Use specific service restarts when possible**
   ```bash
   make restart-backend  # Instead of make restart
   ```

3. **Monitor services during operations**
   ```bash
   make monitor
   ```

4. **Run tests after changes**
   ```bash
   make test
   ```

5. **Check logs for issues**
   ```bash
   make logs-backend
   make logs-frontend
   ```

## Safety Notes

⚠️ **DANGEROUS COMMANDS** - Use with extreme caution:
- `make db-reset` - Removes all database data
- `make clean-volumes` - Removes all Docker volumes
- `make clean-all` - Removes all containers, images, and volumes
- `make emergency-stop` - Force kills all services

Always backup your data before using these commands!

## Customization

You can extend the Makefile by adding your own commands. Follow the existing pattern:

```makefile
your-command: ## Description of your command
	your-command-here
```

The `##` comment format is used by the `make help` command to display command descriptions.
