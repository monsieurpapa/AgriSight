# Windows Make Setup Guide

## Overview
This guide explains how to install and use Make on Windows to take advantage of the comprehensive Makefile provided with the AgriSight platform.

## Option 1: Install Make via Chocolatey (Recommended)

### Step 1: Install Chocolatey
Open PowerShell as Administrator and run:
```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
```

### Step 2: Install Make
```powershell
choco install make
```

### Step 3: Verify Installation
```powershell
make --version
```

## Option 2: Install Make via Scoop

### Step 1: Install Scoop
```powershell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
irm get.scoop.sh | iex
```

### Step 2: Install Make
```powershell
scoop install make
```

## Option 3: Install Make via MSYS2

### Step 1: Download and Install MSYS2
1. Go to https://www.msys2.org/
2. Download and install MSYS2
3. Open MSYS2 terminal

### Step 2: Install Make
```bash
pacman -S make
```

### Step 3: Add to PATH
Add `C:\msys64\usr\bin` to your Windows PATH environment variable.

## Option 4: Use Windows Subsystem for Linux (WSL)

### Step 1: Install WSL
```powershell
wsl --install
```

### Step 2: Install Make in WSL
```bash
sudo apt update
sudo apt install make
```

## Alternative: Use Provided Scripts

If you prefer not to install Make, you can use the provided Windows scripts:

### Batch Script (agrisight.bat)
```cmd
# Show help
agrisight.bat help

# Start services
agrisight.bat up

# View logs
agrisight.bat logs

# Check status
agrisight.bat status
```

### PowerShell Script (agrisight.ps1)
```powershell
# Show help
.\agrisight.ps1 help

# Start services
.\agrisight.ps1 up

# View logs
.\agrisight.ps1 logs

# Check status
.\agrisight.ps1 status
```

## Using Make Commands

Once Make is installed, you can use all the commands from the Makefile:

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

# Check service health
make health-check
```

### Development Commands
```bash
# Run tests
make test

# Run migrations
make migrate

# Create superuser
make createsuperuser

# Format code
make format-backend
make format-frontend
```

### Maintenance Commands
```bash
# Backup database
make backup-db

# Clean Docker system
make clean-docker

# Update dependencies
make update-deps

# Security check
make security-check
```

## Troubleshooting

### Make Command Not Found
If you get "make: command not found", ensure:
1. Make is properly installed
2. The installation directory is in your PATH
3. You've restarted your terminal/command prompt

### Permission Issues
If you encounter permission issues:
1. Run your terminal as Administrator
2. Check your execution policy: `Get-ExecutionPolicy`
3. Set execution policy if needed: `Set-ExecutionPolicy RemoteSigned`

### Docker Issues
If Docker commands fail:
1. Ensure Docker Desktop is running
2. Check Docker daemon status
3. Verify Docker Compose is installed

## Recommended Setup

For the best experience on Windows:

1. **Install Docker Desktop** - Required for the platform
2. **Install Make via Chocolatey** - For easy command management
3. **Use Windows Terminal** - For better terminal experience
4. **Install Git for Windows** - For version control

## Quick Start Commands

```bash
# Initial setup
make setup

# Create admin user
make createsuperuser

# Start platform
make up

# Check health
make health-check

# View logs
make logs
```

## Benefits of Using Make

1. **Consistency** - Same commands work across all platforms
2. **Comprehensive** - 50+ commands for all operations
3. **Documentation** - Built-in help with `make help`
4. **Efficiency** - Quick access to complex operations
5. **Maintenance** - Easy backup, restore, and cleanup operations

## Support

If you encounter issues:
1. Check the [Makefile Usage Guide](MAKEFILE_USAGE.md)
2. Use the alternative batch/PowerShell scripts
3. Refer to Docker Compose documentation for direct commands
4. Check the platform logs with `make logs` or `agrisight.bat logs`
