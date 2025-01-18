# Docker Infrastructure

The GenAI Launchpad's Docker infrastructure transforms a complex, multi-service application into an easily manageable development and deployment environment. This guide explains how our containerized architecture works and how to make the most of it.

## Understanding the Architecture

At its foundation, the GenAI Launchpad operates through four essential services working in harmony:

The **FastAPI Application** serves as your system's front door, handling all incoming HTTP requests with the efficiency and type safety that FastAPI is known for. Behind this, the **Celery Worker** processes your AI tasks asynchronously, ensuring your application remains responsive even during complex operations. These services are supported by **PostgreSQL**, which not only stores your traditional data but also manages vector embeddings for AI operations, and **Redis**, which orchestrates communication between your API and workers through its robust message broker capabilities.

## Development Workflow

Getting started with development is straightforward. From your project root, simply run:

```bash
cd docker
./start.sh
```

This script orchestrates a carefully sequenced startup process:

1. First, it establishes isolated Docker networks for secure service communication
2. Then, it initializes PostgreSQL and Redis, ensuring your data services are ready
3. Finally, it launches the API and worker services with hot-reloading enabled

### Real-time Development Experience

The development environment is crafted for an optimal developer experience. When you modify your code, the system automatically:

- Reloads your API server to reflect changes immediately
- Restarts workers to pick up new task definitions
- Preserves your database state between restarts

To monitor your application in real-time, use:

```bash
cd docker
./logs.sh
```

This command provides a unified view of all container logs, with timestamps and color coding for easy debugging.

## Configuration Management

Configuration follows the [12-factor app](https://12factor.net/) methodology, using environment variables for all settings. Start by creating your environment file:

```bash
cp docker/.env.example docker/.env
```

The configuration system supports multiple environments through different .env files:

- `.env.development` for local development
- `.env.staging` for testing environments
- `.env.production` for production deployments

## Local Development Options

The infrastructure supports flexible development approaches. You can run the entire stack in containers, or mix local and containerized services for faster development cycles:

```bash
# Run dependencies in containers
docker-compose up database redis

# Run API locally for faster development
cd app
uvicorn main:app --reload

# Run worker locally for easier debugging
celery -A config.celery_config worker --loglevel=INFO
```

This hybrid approach gives you the best of both worlds:

- Containerized dependencies for consistency
- Local service execution for faster feedback
- Full IDE debugging capabilities
- Immediate code reloading

## Production Deployment

The production environment builds upon the development setup with additional security and reliability features:

### Security Enhancements
- [Caddy](https://caddyserver.com/) server handles SSL/TLS termination automatically
- Services run as non-root users
- Network isolation between containers
- Secure credential management through environment variables

### Reliability Features
- Persistent volume mounts for data durability
- Container resource limits to prevent resource exhaustion
- Health checks for automatic container recovery
- Structured logging for better observability

### Resource Management
- Configurable CPU and memory limits
- Volume mounts for data persistence
- Automatic container recovery
- Load balancing capabilities

The production setup is designed to be both secure and maintainable, following Docker best practices and security guidelines. It provides a solid foundation for running your AI applications in any production environment, from single-server deployments to complex cloud infrastructures.

The Docker infrastructure is designed to grow with your needs, from initial development to production deployment, while maintaining consistency and security throughout the application lifecycle.