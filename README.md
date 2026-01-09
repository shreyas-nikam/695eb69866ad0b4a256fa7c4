# QuLab: Foundation & Platform Setup for Individual AI-Readiness Platform

![QuantUniversity Logo](https://www.quantuniversity.com/assets/img/logo5.jpg)

## Project Title and Description

Welcome to **QuLab: Foundation & Platform Setup**, an interactive Streamlit application designed as a laboratory project for establishing the robust foundation of an **Individual AI-Readiness Platform**. This lab guides software developers through the critical initial steps of building a production-ready AI service, focusing on best practices in Python development, API design, configuration management, and operational reliability.

The core objective is to lay down a scalable, maintainable, and secure project skeleton for future AI services. Through hands-on simulations within this Streamlit interface, participants will learn how to leverage modern Python tools and frameworks to prevent common pitfalls, streamline development workflows, and ensure the consistency and compliance of AI applications from day one. This lab is a blueprint for rapidly establishing resilient AI services capable of adapting to the fast-evolving AI landscape.

## Features

This interactive lab covers the following key functionalities and learning objectives:

*   **Interactive Workflow**: Guides users through a real-world project setup process using a step-by-step, interactive interface.
*   **Project Initialization**: Demonstrates the use of Poetry for dependency management and establishing a standardized, scalable directory structure for AI services (`src/air/{api/routes/v1,config,models,services,schemas,agents,observability}`).
*   **Robust Configuration System**: Implements a type-safe and validated configuration system using Pydantic v2 and `pydantic-settings`.
    *   **Custom Validation**: Enforces complex business rules (e.g., ensuring AI model scoring weights sum to 1.0) using Pydantic's `model_validator`.
    *   **Secure Secret Handling**: Utilizes `SecretStr` to prevent accidental exposure of sensitive API keys and credentials.
*   **FastAPI Application Core**: Builds a foundational FastAPI application with:
    *   **Application Factory Pattern**: For creating configurable FastAPI instances.
    *   **API Versioning**: Demonstrates versioned API routers (`/api/v1`, `/api/v2`) for future-proofing and backward compatibility.
    *   **Middleware Implementation**: Includes CORS, request ID tracking (`X-Request-ID`), and request timing (`X-Process-Time`) middleware for enhanced observability and security.
    *   **Graceful Lifespan Management**: Uses `asynccontextmanager` for proper resource initialization and cleanup during application startup and shutdown.
*   **Comprehensive Health Checks**: Implements various health check endpoints crucial for production deployment:
    *   `/health`: Basic application responsiveness check.
    *   `/health/detailed`: In-depth status of internal and external dependencies (database, Redis, LLM API).
    *   `/health/ready`: Readiness probe for container orchestration (e.g., Kubernetes) to indicate if the service is ready to accept traffic.
    *   `/health/live`: Liveness probe to determine if the application process is still active and responsive.
*   **Common Mistakes & Troubleshooting**: Explores and demonstrates how to prevent critical errors such as:
    *   Invalid configuration (e.g., incorrect weight sums).
    *   Exposure of sensitive secrets in logs.
    *   Resource leaks due to improper shutdown procedures.

## Getting Started

To get this Streamlit application up and running on your local machine, follow these instructions.

### Prerequisites

*   **Python 3.12+**: The lab project is designed and tested with Python 3.12.
*   **Poetry**: Recommended for dependency management. If you don't have it, install it via:
    ```bash
    pip install poetry
    ```
*   **Git**: For cloning the repository.

### Installation

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/quantuniversity/qu-lab-ai-platform-setup.git
    cd qu-lab-ai-platform-setup
    ```
    *(Note: Replace `quantuniversity/qu-lab-ai-platform-setup.git` with the actual repository URL if different.)*

2.  **Install dependencies using Poetry**:
    If you're using Poetry, navigate to the project directory and install the dependencies:
    ```bash
    poetry install
    ```
    This will create a virtual environment and install all project dependencies.

3.  **Activate the virtual environment (if not using Poetry shell)**:
    If you installed with Poetry and are not using `poetry shell`, you might need to activate the virtual environment manually to ensure `streamlit` runs within it:
    ```bash
    poetry shell
    # or (if you know the path to your venv)
    # source .venv/bin/activate
    ```
    If you are not using Poetry, ensure all requirements from `pyproject.toml` (or `requirements.txt` if provided) are installed in your active Python environment:
    ```bash
    pip install streamlit fastapi uvicorn pydantic pydantic-settings httpx sse-starlette
    ```

## Usage

1.  **Run the Streamlit application**:
    From the project's root directory (with your virtual environment activated), execute:
    ```bash
    streamlit run app.py
    ```
    This will open the Streamlit application in your default web browser.

2.  **Navigate Through Tasks**:
    Use the **sidebar navigation** on the left to explore different tasks of the AI-Readiness Platform setup. Each task presents a problem statement, real-world relevance, and interactive buttons to simulate code execution and view outputs.

3.  **Interact with the Lab**:
    Click the provided buttons (e.g., "Simulate Project Initialization", "Load and Validate Settings", "Create FastAPI Application", "Run Health Checks") to trigger the simulation of various development steps and observe their outputs.

## Project Structure

The lab project itself is structured to be easily navigable. The underlying *simulated* AI-Readiness Platform project (the one being built in the lab) follows a robust, scalable architecture:

```
.
├── app.py                      # Main Streamlit application file
├── source.py                   # Backend logic for Settings, FastAPI app factory, and health checks
├── pyproject.toml              # Poetry project configuration and dependencies
├── .env.example                # Example environment variables for configuration
└── src/air/                    # (Simulated) Core application logic for the AI-Readiness Platform
    ├── __init__.py             # Python package initializer
    ├── api/                    # API definitions
    │   ├── routes/             # API route definitions
    │   │   ├── v1/             # Version 1 API routes
    │   │   └── v2/             # Version 2 API routes
    │   └── __init__.py
    ├── config/                 # Configuration files (e.g., settings models)
    ├── models/                 # Data models (e.g., ORM models, Pydantic models for data persistence)
    ├── schemas/                # Pydantic schemas for request/response validation
    ├── services/               # Business logic and service layer components
    ├── agents/                 # AI agents or specific model interaction logic
    ├── observability/          # Tracing, logging, monitoring setup
    ├── mcp/                    # (Placeholder) Micro-Control Plane or orchestration
    ├── events/                 # Event definitions and handlers
    └── ...
├── tests/                      # (Simulated) Test suite
│   ├── unit/
│   ├── integration/
│   └── evals/                  # Evaluation tests for AI models
├── docs/                       # (Simulated) Documentation
│   ├── adr/                    # Architecture Decision Records
│   ├── requirements/
│   └── failure-modes/
└── Dockerfile                  # (Conceptual) Dockerfile for containerization
```

*   `app.py`: This is the Streamlit file you run. It orchestrates the interactive lab experience.
*   `source.py`: Contains the actual Python code snippets and functions that are "executed" or simulated within the Streamlit app. This includes the `Settings` class, `create_app_notebook`, `health_check_func`, etc.
*   The `src/air/` directory and its subdirectories represent the *ideal* project structure that the lab advocates for, promoting modularity, separation of concerns, and scalability for real-world AI services.

## Technology Stack

The lab and the conceptual AI-Readiness Platform leverage a modern and robust technology stack:

*   **Python 3.12**: The primary programming language and runtime environment.
*   **Streamlit**: For building the interactive, web-based laboratory interface.
*   **Poetry**: For reproducible dependency management, virtual environment creation, and packaging.
*   **FastAPI**: A high-performance, asynchronous web framework for building the API services.
*   **Pydantic v2**: For data validation, settings management, and defining clear data schemas.
*   **Pydantic-Settings**: Extension for Pydantic to manage application settings from environment variables or `.env` files.
*   **Uvicorn**: An ASGI server to run FastAPI applications efficiently.
*   **Httpx**: A next-generation HTTP client (used for simulated external API calls).
*   **Sse-starlette**: For Server-Sent Events (if needed for real-time updates).
*   **Docker**: (Mentioned as a tool) For containerization and ensuring reproducible deployment environments.

### Development Tools (Simulated dependencies)

*   **Pytest**: For testing (unit, integration, evaluation).
*   **pytest-asyncio**: For testing asynchronous code.
*   **pytest-cov**: For test coverage reporting.
*   **Black**: An uncompromising Python code formatter.
*   **Ruff**: An extremely fast Python linter, written in Rust.
*   **Mypy**: A static type checker for Python.
*   **Hypothesis**: A powerful property-based testing library.

## Contributing

As this is a lab project, direct contributions might not be the primary focus. However, if you find any bugs, have suggestions for improvements, or wish to contribute to making this lab even better, please feel free to:

1.  **Fork the repository**.
2.  **Create a new branch** (`git checkout -b feature/your-feature-name` or `bugfix/your-bugfix-name`).
3.  **Make your changes**.
4.  **Commit your changes** (`git commit -m 'feat: Add new feature'`).
5.  **Push to your branch** (`git push origin feature/your-feature-name`).
6.  **Open a Pull Request** with a clear description of your changes.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
*(Note: You might need to create a `LICENSE` file if it doesn't exist yet.)*

## Contact

For any questions, feedback, or further information about QuantUniversity and its programs, please visit:

*   **Website**: [www.quantuniversity.com](https://www.quantuniversity.com)
*   **Email**: `info@quantuniversity.com`
