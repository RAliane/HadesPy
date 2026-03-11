# HadesPy: AI Agent Full Stack

[![Python](https://img.shields.io/badge/Python-3.12+-blue?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Gradio](https://img.shields.io/badge/Gradio-FF6B6B?logo=gradio&logoColor=white)](https://gradio.app/)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Podman](https://img.shields.io/badge/Podman-89D4C8?logo=podman&logoColor=white)](https://podman.io/)
[![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![GitLab CI](https://img.shields.io/badge/GitLab_CI-FC6D26?logo=gitlab&logoColor=white)](https://about.gitlab.com/stages-devops-lifecycle/continuous-integration/)
[![Directus](https://img.shields.io/badge/Directus-2F7BC2?logo=directus&logoColor=white)](https://directus.io/)
[![License](https://img.shields.io/badge/License-MIT-green)](https://opensource.org/licenses/MIT)

Welcome to HadesPy, an end-to-end AI agent system designed to be user-friendly and secure.

## Introduction

HadesPy is a comprehensive AI agent system that combines several technologies to provide a robust and secure platform for AI applications. It is designed to be easy to use, even for those who are not familiar with advanced technical concepts.

## Features

- **Real-time Collaboration**: Work with AI agents in real-time.
- **Local Models**: Use local models with Ollama or add your own API keys for different model providers.
- **Secure Environment**: Operates in a zero-trust environment with triple-layer networks, ensuring data security.
- **Easy Deployment**: Can be easily deployed on Render as a service or locally using Docker/Podman.
- **Customizable**: Add your own connectors through API keys.
- **Smart Memory**: Access to Cognee AI smart memory, caching, and rate limiting.
- **User-Friendly Interfaces**: Choose between Gradio and Streamlit for a user-friendly experience.

## Prerequisites

Before you start, make sure you have the following:
- ![Python](https://img.shields.io/badge/Python-3.12+-blue?logo=python&logoColor=white) Python 3.12 or higher
- ![UV](https://img.shields.io/badge/UV-Package_Manager-000000?logo=python&logoColor=white) UV package manager
- ![Podman](https://img.shields.io/badge/Podman-89D4C8?logo=podman&logoColor=white) Podman and podman-compose **or** ![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white) Docker
- (Optional) A Linux server for deployment

## Installation

### For Windows Users (WSL)

1. **Install WSL**:
   Follow the [official guide](https://learn.microsoft.com/en-us/windows/wsl/install) to install Windows Subsystem for Linux.

2. **Set Up WSL**:
   ```bash
   wsl --install
   wsl --set-default-version 2
   ```

3. **Install Prerequisites**:
   ```bash
   sudo apt update
   sudo apt install python3.12 python3-pip
   ```

### Step 1: Clone the Repository
First, clone the repository to your local machine:

```bash
git clone https://github.com/RAliane/HadesPy.git
cd HadesPy
```

### Step 2: Run the Bootstrap Script
Run the bootstrap script to set up the environment:

```bash
chmod +x scripts/bootstrap.sh
./scripts/bootstrap.sh
```

### Step 3: Configure the Environment
Edit the environment configuration file:

```bash
vim .env
```

## Usage

### Local Development

1. **Install Dependencies**:
   ```bash
   uv sync
   ```

2. **Run the FastAPI Server**:
   ```bash
   uv run uvicorn src.main:app --reload
   ```

3. **Run the Gradio UI** (in another terminal):
   ```bash
   uv run python -m src.ui_gradio
   ```

   Or run the Streamlit UI:
   ```bash
   uv run streamlit run src/ui_streamlit.py
   ```

### Using Ollama

To use local models with Ollama:

1. **Install Ollama**:
   Follow the instructions at [Ollama's official site](https://ollama.ai/).

2. **Pull a Model**:
   ```bash
   ollama pull llama3
   ```

3. **Configure HadesPy**:
   Update your `.env` file to use the Ollama model:
   ```env
   OLLAMA_MODEL=llama3
   ```

### Containerization with Podman/Docker

1. **Build the Image**:
   ```bash
   podman-compose build
   # or
   docker-compose build
   ```

2. **Start All Services**:
   ```bash
   podman-compose up -d
   # or
   docker-compose up -d
   ```

3. **View Logs**:
   ```bash
   podman-compose logs -f api
   # or
   docker-compose logs -f api
   ```

4. **Scale API Workers**:
   ```bash
   podman-compose up -d --scale api=3
   # or
   docker-compose up -d --scale api=3
   ```

## Configuration

### Environment Variables

You can configure the system using environment variables. Here are some common variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `APP_ENV` | `development` | Environment mode |
| `FASTAPI_PORT` | `8000` | API server port |
| `DIRECTUS_URL` | `http://localhost:8055` | Directus endpoint |
| `COGNEE_EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | Embedding model |
| `OPENAI_API_KEY` | - | OpenAI API key |
| `OLLAMA_MODEL` | - | Ollama model name |

For a full list of environment variables, see `.env.example`.

## Security

HadesPy is designed with security in mind:
- **Firewall**: UFW firewall is configured to allow only necessary ports.
- **Fail2Ban**: Protects against brute force attacks and API abuse.
- **Podman/Docker Security**: Uses rootless containers, user namespaces, and network isolation.

## Monitoring

HadesPy includes monitoring tools to help you keep an eye on the system:
- **Prometheus Metrics**: Monitor API performance.
- **Grafana Dashboards**: Visualize system metrics.

## Support and Community

If you need help or have questions, you can:
- Report issues on the GitHub Issues page.
- Join our community forum for support and discussions.

## License

This project is licensed under the MIT License.