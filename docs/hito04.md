# Hito 4: Composition of Services

Student: **Niklas Schuerrle**  
Email: **niklas733@correo.ugr.es**  
Project: **ExpenseTracker**

---

## CI Status

![CI](https://github.com/niklas3739/ExpenseTracker/actions/workflows/ci.yml/badge.svg)

---

## Overview Milestone 4

The goal of this milestone is to **containerize the entire ExpenseTracker application** and design a **multi-service architecture** using Docker and Docker Compose.  
The result is a reproducible and portable deployment environment that runs the database, backend microservice, and frontend application as a coordinated cluster.

This milestone includes:

- Containerizing the backend API, frontend React SPA, and database.
- Creating a complete `compose.yaml` describing their relationships, networking, and volumes.
- Publishing Docker images to **GitHub Packages** automatically.
- Adding an automated test that builds the cluster and checks that the API responds properly.

The final outcome is a production-like microservice deployment that can run anywhere with Docker.

---

## Structure and justification of the service cluster

The ExpenseTracker system is composed of **three containers**, each representing a distinct concern:

### 1. Backend API (FastAPI)
- Provides all REST endpoints for groups, expenses, settlements and balances.  
- Built from a minimal `python:3.11-slim` base image with Uvicorn as the ASGI server.  
- Connects to PostgreSQL using environment variables.  
- Exposes a `/health` endpoint for automated testing.

### 2. Frontend (React + Nginx)
- The React SPA is built in a Node container and statically served by Nginx.  
- Nginx proxies all `/api` requests to the backend container.  
- Mirrors a real production setup where backend and frontend are decoupled.

### 3. Database (PostgreSQL)
- A dedicated container acting solely as a data store.  
- Uses a Docker volume (`db_data`) for persistent storage.  
- Satisfies the milestone requirement of having a data-only container.

These services are orchestrated through Docker Compose, forming a reproducible and fully isolated cluster.

---

## Configuration of each container and justification

### Backend Container
**Base image:** `python:3.11-slim`

**Responsibilities:**
- Install application dependencies from `requirements.txt`.
- Copy the FastAPI application into the container.
- Expose port 8000 and run Uvicorn with the correct app module.
- Connect to PostgreSQL via environment variables.

**Justification:**
- Slim Python images reduce size and attack surface.
- Uvicorn provides high-performance async serving, ideal for microservices.

---

### Frontend Container
**Base images:**
1. `node:20-alpine` for build stage  
2. `nginx:1.27-alpine` for runtime stage

**Responsibilities:**
- Build React app using CRA.
- Serve static files using Nginx.
- Proxy `/api` to the backend container using Nginx config.

**Justification:**
- Multi-stage builds drastically reduce final image size.
- Nginx is optimized for static file hosting and reverse-proxy setups.

---

### Database Container (PostgreSQL)

**Base image:** `postgres:15-alpine`

**Responsibilities:**
- Provide persistent relational storage.
- Expose internal port 5432 to the cluster.
- Store data in a Docker volume (`db_data`).

**Justification:**
- PostgreSQL integrates seamlessly with SQLModel/SQLAlchemy.
- A data-only container satisfies the requirement for persistent storage.

---

## Dockerfiles for the microservices

Two Dockerfiles were implemented:

### Backend Dockerfile  
Location: `expense_tracker/api/Dockerfile`  
Contains:
- Slim Python base  
- System dependencies  
- Requirements installation  
- App copy  
- Uvicorn command  

### Frontend Dockerfile  
Location: `frontend/Dockerfile`  
Contains:
- Node build stage  
- Nginx runtime stage  
- SPA build and deployment  
- API proxy configuration through Nginx  

Both Dockerfiles build successfully and are used by `compose.yaml`.

---

## Publishing containers to GitHub Packages

A dedicated CI workflow (`.github/workflows/docker.yml`) builds and publishes:

- `ghcr.io/<user>/expense-tracker-api`
- `ghcr.io/<user>/expense-tracker-frontend`

Each push produces:
- A `latest` image
- A commit-SHA-tagged image

This fulfills the milestone requirement of automatic container publishing.

---

## Documentation of `compose.yaml`

The `compose.yaml` in the project root defines:

- **Three services:** `api`, `frontend`, `db`
- **One network:** `expense_net`
- **One persistent volume:** `db_data`
- **Environment variables** for database connectivity
- **Port mappings:**  
  - Backend → `8000:8000`  
  - Frontend → `8080:80`
- **Startup order** (`depends_on`)
- **Healthcheck** for the API

This file provides a complete and reproducible environment for development and testing.

---

## Automated cluster test

A new Makefile target was added:

```bash
make test-compose
```

This command:
1. Builds all services
2. Starts the full cluster using `docker compose up`
3. Waits for initialization
4. Executes a live API check:
    ```bash
    curl -f http://localhost:8000/health
    ```
5. Fails with container logs if any service fails to start

## Continuous integration and automation
The workflow file `docker.yml` ensures that:
- Docker Buildx is configured
- The repository logs into GitHub Container Registry
- API and frontend images are built and published
- The workflow runs automatically on each push

Combined with the existing CI for testing, the project now has full automated validation and publishing of all microservices.

---

- [Find the Docker configuration here](../.github/workflows/docker.yml)  
- [Find the Backend Dockerfile here](.././expense_tracker/api/Dockerfile)  
- [Find the Frontend Dockerfile here](.././frontend/Dockerfile)

---

## Screenshots
- [Test execution via CI](screenshots/build_and_push_pipeline.png)