# QuLab: InnovateAI Platform Foundation & Platform Setup Lab

![QuantUniversity Logo](https://www.quantuniversity.com/assets/img/logo5.jpg)

## Project Overview

This repository hosts the Streamlit-based interactive lab for **QuLab: Foundation & Platform Setup**, a project designed to guide developers through establishing a robust, maintainable, and scalable backend foundation for the "Predictive Intelligence Engine" (PIE), also referred to as the "Individual AI-R Platform" (v4.0.0). This lab simulates the foundational work of a Senior Software Engineer at InnovateAI Solutions, covering critical aspects of modern Python application development.

The Streamlit interface acts as an interactive learning environment, demonstrating key concepts such as project structure, configuration management with Pydantic v2, building a FastAPI application core with middleware, and implementing API versioning. It aims to showcase best practices for creating a production-ready AI platform.

### Key Objectives of the Lab

*   **Repository Setup**: Initialize a monorepo structure using Poetry.
*   **Configuration**: Implement a resilient configuration system with Pydantic v2, including data validation and sensitive data handling.
*   **API Scaffold**: Build the core FastAPI application with essential middleware and application lifecycle management.
*   **API Versioning**: Establish a clear strategy for API versioning to support evolutionary development.
*   **Production Readiness (Conceptual)**: Outline strategies for Docker containerization and CI/CD pipelines using GitHub Actions.

## Features

This lab highlights and interactively demonstrates the following core features and concepts:

*   **Interactive Streamlit Interface**: A user-friendly web interface to navigate through lab sections and interact with configuration settings.
*   **Pydantic v2 Configuration System**:
    *   Robust settings management loading from `.env` files.
    *   Type checking and validation for all application parameters.
    *   Use of `SecretStr` for secure handling of sensitive API keys (e.g., OpenAI, Anthropic).
    *   Custom `model_validator` to enforce complex business rules, such as ensuring AI scoring weights sum to 1.0.
*   **FastAPI Application Core**:
    *   Implementation of the **Application Factory Pattern** for flexible application creation.
    *   **Application Lifespan Management**: Graceful startup and shutdown of resources using FastAPI's `lifespan` context manager.
    *   **CORS Middleware**: Configuration for Cross-Origin Resource Sharing to allow secure cross-domain requests.
    *   **Custom Request Timing Middleware**: Demonstrates how to add a unique request ID and measure processing time for every API request, enhancing observability.
*   **API Versioning**:
    *   Strategic use of `APIRouter` instances with distinct URL prefixes (`/api/v1`, `/api/v2`) to enable backward compatibility and phased API evolution.
    *   Conceptual `v1` and `v2` status endpoints.
*   **Health Check Endpoint**: A basic `/health` endpoint to monitor application status.
*   **Conceptual Production Readiness**: Discusses the integration of Docker for containerization and GitHub Actions for CI/CD pipelines (linting, testing, coverage).
*   **Common Mistakes & Troubleshooting**: Dedicated section addressing frequent pitfalls in backend development and how the demonstrated patterns mitigate them.

## Getting Started

This section provides instructions on how to set up and run the Streamlit lab application locally.

### Prerequisites

Before you begin, ensure you have the following installed:

*   **Python 3.12+**: The application leverages features specific to newer Python versions.
*   **Poetry**: A Python dependency management and packaging tool. If not installed, you can get it via `pip install poetry` or follow the official documentation.
*   **Basic Command Line Knowledge**: Familiarity with `cd`, `mkdir`, etc.
*   **Understanding of REST APIs**: Basic concepts of HTTP methods and API interactions.

### Installation

1.  **Clone the Repository**:
    ```bash
    git clone https://github.com/your-username/qulab-ai-platform-setup.git
    cd qulab-ai-platform-setup
    ```
    *(Note: Replace `https://github.com/your-username/qulab-ai-platform-setup.git` with the actual repository URL)*

2.  **Initialize Poetry Environment and Install Dependencies**:
    ```bash
    poetry install
    ```
    This command will create a virtual environment and install all project dependencies, including FastAPI, Pydantic, Streamlit, and development tools.

3.  **Create a `.env` File (Optional but Recommended)**:
    For demonstrating the Pydantic settings system, especially with sensitive values, create a `.env` file in the project root.
    ```
    # .env example
    APP_ENV=development
    DEBUG=True
    OPENAI_API_KEY="sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    ANTHROPIC_API_KEY="sk-ant-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    DAILY_COST_BUDGET_USD=150.0
    W_FLUENCY=0.45
    W_DOMAIN=0.35
    W_ADAPTIVE=0.20
    ```
    *(Note: The Streamlit app can simulate these values interactively without a physical `.env` file, but for a real FastAPI app, it's standard practice.)*

## Usage

### Running the Streamlit Lab Application

To launch the interactive lab environment:

1.  **Activate the Poetry Shell**:
    ```bash
    poetry shell
    ```

2.  **Run the Streamlit Application**:
    ```bash
    streamlit run app.py
    ```

    This will open the Streamlit application in your default web browser (usually at `http://localhost:8501`).

### Navigating the Lab

Once the Streamlit app is running:

*   Use the **"Navigate Lab Sections"** dropdown in the sidebar to move between different parts of the lab (Overview, Project Initialization, Configuration System, FastAPI Core, API Versioning, Production Readiness, Troubleshooting).
*   **"2. Configuration System"**: Interact with input fields to test Pydantic's validation and `SecretStr` behavior. Click "Validate Configuration" to see instant feedback.
*   **"3. FastAPI Application Core"**: Click "Simulate App Startup & Shutdown" to observe the conceptual lifecycle events managed by FastAPI's `lifespan`.
*   Explore the other sections for conceptual explanations and code examples.

### Conceptual FastAPI Server (Not run directly by `app.py`)

While `app.py` runs the Streamlit interface, the actual FastAPI application (`src/air/api/main.py` conceptually) would be run using `uvicorn`:

```bash
# In a separate terminal, after 'poetry shell'
uvicorn src.air.api.main:app --host 0.0.0.0 --port 8000 --reload
```
*(Note: The actual `main.py` for FastAPI would be within the `src/air/api` directory, as per the project structure discussed in the lab. This command is illustrative; `app.py` does not launch a separate FastAPI server.)*

## Project Structure

The project follows a modular, monorepo-style structure designed for scalability and clear separation of concerns, as outlined in the lab:

```
.
├── .github/                 # GitHub Actions CI/CD workflows (conceptual)
│   └── workflows/
│       └── ci.yml
├── src/                     # Source code directory
│   └── air/                 # Main application package
│       ├── api/             # API related components
│       │   ├── routes/      # API endpoints
│       │   │   ├── v1/      # Version 1 API routes
│       │   │   └── v2/      # Version 2 API routes
│       │   └── main.py      # Main FastAPI application entry point (conceptual)
│       ├── agents/          # AI agents/orchestrators
│       ├── config/          # Application configuration (e.g., settings.py)
│       ├── events/          # Event handling and messaging
│       ├── mcp/             # Microservices Control Plane / central orchestrator
│       ├── models/          # Data models (Pydantic, database ORM)
│       ├── observability/   # Logging, monitoring, tracing setup
│       ├── schemas/         # Pydantic schemas for request/response bodies
│       └── services/        # Business logic services
├── tests/                   # Test suite
│   ├── evals/               # Evaluation tests for AI models
│   ├── integration/         # Integration tests
│   └── unit/                # Unit tests
├── .env                     # Environment variables (example, sensitive data)
├── app.py                   # The Streamlit lab application
├── pyproject.toml           # Poetry project definition and dependencies
├── README.md                # This file
└── Dockerfile               # Docker container definition (conceptual)
└── docker-compose.yml       # Docker Compose for local development (conceptual)
```

## Technology Stack

This lab demonstrates a foundation built upon cutting-edge Python technologies:

*   **Python**: Version 3.12+
*   **Streamlit**: For the interactive lab interface.
*   **FastAPI**: A modern, fast (high-performance) web framework for building APIs with Python 3.8+ based on standard Python type hints.
*   **Pydantic v2**: Data validation and settings management using Python type hints.
*   **Pydantic-Settings**: Extends Pydantic for convenient configuration management, including `.env` file support.
*   **Uvicorn**: An ASGI web server for running FastAPI applications.
*   **Poetry**: For dependency management and project packaging.
*   **httpx**: A fully featured HTTP client for Python, often used for making requests.
*   **sse-starlette**: Server-Sent Events (SSE) for Starlette/FastAPI.
*   **Conceptual Tools**: Docker (Containerization), GitHub Actions (CI/CD).
*   **Development Tools**: `pytest`, `pytest-asyncio`, `pytest-cov`, `black`, `ruff`, `mypy`.

## Contributing

This project is primarily a lab for educational purposes. However, if you find any issues or have suggestions for improvements, please feel free to:

1.  **Fork** the repository.
2.  **Create a new branch** (`git checkout -b feature/your-feature-name`).
3.  **Make your changes**.
4.  **Commit your changes** (`git commit -m 'feat: Add new feature'`).
5.  **Push to the branch** (`git push origin feature/your-feature-name`).
6.  **Open a Pull Request**.

Please ensure your code adheres to standard Python best practices and includes appropriate comments.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details (if applicable).

## Contact

For questions, feedback, or support regarding this lab project, please contact:

*   **QuantUniversity Team**
*   **Email**: support@quantuniversity.com
*   **Website**: [www.quantuniversity.com](https://www.quantuniversity.com)

---

Enjoy your journey through building a solid foundation for AI platforms!
