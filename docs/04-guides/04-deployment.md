# Deployment Guide

This guide explains how to deploy the GenAI Launchpad on virtual machines running Linux distributions. We'll cover different cloud providers and deployment strategies to help you choose the best approach for your needs.

## Understanding the Deployment Architecture

The GenAI Launchpad uses a containerized architecture with Docker, making it highly portable across different environments. The system consists of several core services:

- A FastAPI application handling HTTP requests
- Celery workers for background task processing
- PostgreSQL for data persistence and vector storage
- Redis for message queuing and caching
- Caddy for SSL/TLS termination and reverse proxying

This architecture ensures scalability and maintainability while keeping deployment relatively simple through Docker Compose.

## Virtual machine requirements

1. Hardware requirements:
    - minimum 4gb RAM.
2. Software requirements:
    - Docker, docker compose: https://docs.docker.com/engine/install/
    - Git: https://git-scm.com/downloads/linux
    - Any text editor (vim, vi, nano etc.)
3. SSH user with root access.
4. SSH key access to GitHub
   account: https://docs.github.com/en/authentication/connecting-to-github-with-ssh/adding-a-new-ssh-key-to-your-github-account
5. Custom domain that is pointed to your virtual machine.
6. Make sure that the default ports for http and https are not blocked by your firewall. So ports 80 and 443 should be
   publicly accessible. This is mandatory for setting up a SSL certificate.

## Deployment

### Overview

1. SSH into the virtual machine.
2. Clone repository.
3. Set .env files.
4. Build and run.
5. Apply database migrations.
6. Check.

### Step by step

#### 1. SSH into the virtual machine

```bash
ssh username@hostname-or-ip
```

#### 2. Clone your Git repository

```bash
cd /opt
git clone git@github.com:datalumina/genai-launchpad.git
```

#### 3. Create .env files

##### Docker

```bash
cd /opt/genai-launchpad/docker
cp .env.example .env
```

Make sure to update the following variables:

1. DATABASE_PASSWORD (for obvious security reasons)
2. CADDY_DOMAIN: Your custom domain here

##### Backend

```bash
cd /opt/genai-launchpad/app
cp .env.example .env
```

Make sure to update the database password for security reasons.

#### 4. Build and run

Go to the docker folder

```bash
cd /opt/genai-launchpad/docker
```

Make sure the script has execute permission

```bash
sudo chmod +x start.sh
```

Execute script

```bash
./start.sh
```

#### 5. Apply database migrations

Go to the backend folder

```bash
cd /opt/genai-launchpad/app
```

Make sure the script has execute permission

```bash
sudo chmod +x migrate.sh
```

Execute script

```bash
./migrate.sh
```

#### 6. Check

Everything should be up and running now. Run the command following command to check if all docker containers are
running:

```bash
docker ps
```

## Cloud Provider Options

The GenAI Launchpad can be deployed on various cloud providers, each offering different advantages:

### Amazon Web Services (AWS)

- **Recommended Instance**: t3.medium or t3.large
- **Key Benefits**: 
  - Extensive global infrastructure
  - Integration with AWS services like S3 and RDS
  - Free tier available for testing
- **Getting Started**: Launch an EC2 instance with Ubuntu Server LTS

### Microsoft Azure

- **Recommended Instance**: B2s or B2ms
- **Key Benefits**:
  - Strong enterprise integration
  - Comprehensive security features
  - Hybrid cloud capabilities
- **Getting Started**: Deploy a Linux VM through Azure Portal or CLI

### Google Cloud Platform (GCP)

- **Recommended Instance**: e2-medium or e2-standard-2
- **Key Benefits**:
  - Strong AI/ML ecosystem
  - Global network infrastructure
  - Generous free tier
- **Getting Started**: Create a Compute Engine instance with Ubuntu

### Hetzner Cloud

- **Recommended Instance**: CPX31 or CPX41
- **Key Benefits**:
  - Very cost-effective pricing
  - European data centers
  - Simple deployment process
- **Getting Started**: Create a new server via Hetzner Cloud Console

### DigitalOcean

- **Recommended Instance**: Basic or Regular Droplet (4GB RAM)
- **Key Benefits**:
  - Developer-friendly interface
  - Straightforward pricing
  - Built-in monitoring
- **Getting Started**: Create a Droplet with Ubuntu LTS

When choosing a cloud provider, consider factors such as:

- Geographic location and latency requirements
- Budget constraints
- Compliance and data residency requirements
- Existing infrastructure and tooling
- Required scaling capabilities