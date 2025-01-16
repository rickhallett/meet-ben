# GenAI Launchpad

With AI innovation moving beyond the speed of light, your time to develop is now more precious than ever. That’s why we’ve built the GenAI Launchpad – your secret weapon to shipping production-ready AI apps, faster.

## 🚀 Introduction

Welcome to the GenAI Launchpad – your all-in-one repository for building powerful, scalable Generative AI applications. Whether you’re prototyping or deploying at scale, this Docker-based setup has you covered with everything from event-driven architecture to seamless AI pipeline integration.

No need to start from scratch or waste time on repetitive configurations. The GenAI Launchpad is engineered to get you up and running fast, with a flexible design that fits your workflow – all while keeping things production-ready from day one.

> **Note**: This repository has two main branches:
> - [`main`](https://github.com/datalumina/genai-launchpad/tree/main): Contains a complete example implementation to demonstrate the Launchpad's capabilities
> - [`boilerplate`](https://github.com/datalumina/genai-launchpad/tree/boilerplate): A stripped-down version with just the core components, perfect for starting new projects.
>
> We recommend following the Accelerator Course first to understand the example implementation in the `main` branch before exploring the boilerplate branch for your own projects.

## 🎯 Overview

The GenAI Launchpad isn’t just another framework – it’s your shortcut to a production-ready AI infrastructure. Built for speed and control, its modular architecture brings together the best tools and design patterns to help you deploy faster without compromising flexibility.

Here’s what you’re working with:

- FastAPI for lightning-fast API development
- Celery for background task processing
- PostgreSQL to handle all your data, includding embeddings
- Redis for fast task queue management
- Caddy for reverse proxy and automatic HTTPS

All services are containerized using Docker, ensuring consistency across development and deployment environments.

## ⭐ Key Features

- **Event-Driven Architecture**: Built-in support for designing and implementing event-driven systems.
- **AI Pipeline Support**: Pre-configured setup for integrating AI models and pipelines.
- **Scalability**: Designed with scalability in mind, allowing easy expansion as your application grows.
- **Flexibility**: Modular architecture that allows for easy customization and extension.
- **Production-Ready**: Includes essential components for a production environment, including logging, monitoring, and security features.
- **Rapid Development**: Boilerplate code and project structure to accelerate development.
- **Docker-Based Deployment**: Complete Docker-based strategy for straightforward deployment.

## 📚 Documentation

While the code is already properly documented, we also included a dedicated `docs` folder in the repository. The documentation covers everything from initial setup through advanced topics like vector storage, LLM integration, and deployment strategies, organized into five main sections (Getting Started, Architecture, Core Components, Guides, and Concepts). For a complete overview and navigation through all topics, see the [documentation index](docs/README.md).

## 🏗️ Project Structure

The Launchpad follows a logical, scalable, and reasonably standardized project structure for building event-driven GenAI apps.

```text
├── app
│   ├── alembic            # Database migration scripts
│   ├── api                # API endpoints and routers
│   ├── config             # Configuration files
│   ├── core               # Components for pipeline and task processing
│   ├── database           # Database models and utilities
│   ├── pipelines          # AI pipeline definitions
│   ├── prompts            # Prompt templates for AI models
│   ├── services           # Business logic and services
│   ├── tasks              # Background task definitions
│   └── utils              # Utility functions and helpers
├── docker                 # Docker configuration files
├── docs                   # Project documentation
├── playground             # Run experiments for pipeline design
└── requests               # Event definitions and handlers
```

## 🚦 Getting Started

We provide two comprehensive guides for setting up the GenAI Launchpad:

- [Quick Start Guide](docs/01-getting-started/03-quick-start.md) - For those following the Accelerator video training or wanting to quickly test the platform
- [Detailed Installation Guide](docs/01-getting-started/02-installation.md) - For production setups, including security considerations and troubleshooting

### Prerequisites

- Git
- Python 3.9 or higher
- Docker (Updated to support docker compose)
- VS Code or Cursor (optional, but recommended)

## 🛠️ Development Workflow

The GenAI Launchpad follows a structured development approach that emphasizes clean architecture and iterative development. Starting with the boilerplate branch, developers can quickly set up their environment, define events, create schemas, and build AI pipelines. The platform includes a playground for experimentation and comprehensive testing utilities to ensure robust implementation.

For detailed instructions, see our [Development Workflow Guide](docs/04-guides/06-development-workflow.md).

## 🎥 Video Tutorials

We offer two video Tutorials to help you master the GenAI Launchpad:

### Accelerator Course
A step-by-step guide through the complete example implementation, perfect for getting started.

- Link: [Accelerator Course Video](https://datalumina.wistia.com/medias/inidp48v10)
- Password: xXH3VzfdiFBToQDuUdeT
- Duration: 70 minutes

### Boilerplate Deep Dive
An in-depth exploration of building projects from scratch using the boilerplate.

- Link: [GenAI Launchpad - Boilerplate](https://datalumina.wistia.com/medias/pd280tdw7s)
- Password: ybAziu4QbyfU44QTrMqU
- Duration: 40 minutes

Both tutorials include instructions and real-world examples to ensure you can effectively leverage the repository for your projects.

## 💬 Support

For support, questions, and collaboration related to the GenAI Launchpad:

1. **Discord Community**: Join our [Discord server](https://discord.gg/H67KUD6vXe) for quick questions, real-time support, and feature discussions. This is the fastest way to get help and connect with other users.

2. **GitHub Issues**: For bug reports and technical problems, please open an issue on our [GitHub repository](https://github.com/datalumina/genai-launchpad/issues). This helps us track issues systematically and builds a searchable knowledge base for the community.

3. **Email**: For private inquiries or matters that don't fit Discord or GitHub, you can reach us at launchpad@datalumina.com. However, we encourage using Discord or GitHub for most support needs to benefit the entire community.

## ⚖️ License

This project is licensed under the DATALUMINA License. See the [LICENSE](/LICENSE) file for details.

### Key Points

- You are free to use this code for personal or commercial projects, including client work.
- You can modify and build upon the code.
- You cannot resell or distribute this code as a template or part of a package where the primary value is in the code itself.
- The software is provided "AS IS", without warranty of any kind.

For the full license text, please refer to the [LICENSE](/LICENSE) file in the repository.

---

For further assistance or to contribute to the GenAI Launchpad, please consult the project maintainers or refer to the contribution guidelines.