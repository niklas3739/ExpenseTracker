# Hito 5: Deployment of the Application on a PaaS

Student: Niklas Schuerrle  
Email: niklas733@correo.ugr.es  
Project: ExpenseTracker  

---
## CI Status

![CI](https://github.com/niklas3739/ExpenseTracker/actions/workflows/ci.yml/badge.svg)

---

## Live Deployment URLs

- **Frontend (Web Application)**  
  https://fe-app-production-0d60.up.railway.app

- **Backend API (FastAPI)**  
  https://be-api-production-4f32.up.railway.app

---

## Overview of Milestone 5

The goal of this milestone is to deploy the ExpenseTracker application to a real cloud environment using a Platform as a Service (PaaS), automate deployments directly from GitHub, and incorporate observability and performance monitoring.

The final result is a fully operational cloud-based application composed of multiple services, deployed in Europe, automatically updated on every push, and monitored in real time.

---

## Choice and Justification of the PaaS Provider

The selected PaaS provider for this milestone is **Railway**.

### Reasons for choosing Railway

- Docker support, allowing reuse of Dockerfiles from previous milestones  
- Direct GitHub integration enabling push-to-deploy workflows  
- Managed PostgreSQL service with persistent storage  
- Built-in observability tools (logs, metrics, restarts)  
- Deployment in European regions, fulfilling legal requirements  
- Simple and transparent configuration suitable for academic projects  

### Alternatives considered

- Render – good Docker support but fewer observability features  
- Fly.io – powerful but more complex networking configuration  
- AWS / GCP – too complex and heavyweight for the scope of this project  

Railway offers the best balance between simplicity, automation, and observability.

---

## Deployed Architecture

The deployed application consists of **three services**:

### 1. PostgreSQL Database

- Managed PostgreSQL instance provided by Railway  
- Stores all application data persistently  
- Exposed to the backend via the `DATABASE_URL` environment variable  

### 2. Backend API (FastAPI)

- Dockerized Python service  
- Exposes REST endpoints for groups, expenses, balances, and settlements  
- Connects to PostgreSQL using SQLModel  
- Health endpoint available at `/health`  

### 3. Frontend (React + Nginx)

- React application built with Create React App  
- Static files served via Nginx  
- Nginx proxies `/api/*` requests to the backend API  
- SPA routing handled with fallback to `index.html`  

This architecture mirrors the local Docker Compose setup, ensuring consistency across environments.

---

## Infrastructure Reproducibility and Configuration

Railway allows infrastructure management via its command-line tool (CLI), ensuring reproducibility without relying solely on manual web configuration.

### Railway CLI usage

    npm install -g @railway/cli
    railway login
    railway link
    railway status
    railway variables

Using these commands, an authorized user can:

- Link the GitHub repository to Railway  
- Inspect deployed services and environment variables  
- Trigger deployments and verify infrastructure state  

All services are built using Dockerfiles stored in the repository, ensuring configuration-as-code.

---

## Automatic Deployment from GitHub

The GitHub repository is directly connected to Railway.

### Deployment workflow

1. Code is pushed to the `main` branch on GitHub  
2. Railway automatically detects the change  
3. Docker images are rebuilt  
4. Services are redeployed without manual intervention  

This establishes a fully automated push-to-deploy pipeline and this behavior was verified by pushing a trivial commit to the main branch and observing the automatic redeployment of both frontend and backend services in Railway.

---

## Observability and Monitoring

Railway provides built-in observability tools that are actively used in this project.

### Logs

- Real-time logs for API and frontend services  
- Used to debug startup issues, routing errors, and runtime failures  

### Metrics

- CPU usage per service  
- Memory consumption  
- Restart and deployment history  

These tools enable fast detection of anomalies and ensure service reliability.

During application usage and stress testing, API logs showed incoming HTTP requests and successful responses. Metrics indicated moderate CPU usage during load tests while memory consumption remained stable, confirming correct behavior under load.

---

## Performance and Stress Testing

Performance and stress testing was conducted against the deployed backend API using the hey HTTP load testing tool.

The health endpoint was tested under concurrent load to evaluate latency, throughput, and stability.

### Example tests

    hey -n 1000 -c 25 https://be-api-production-4f32.up.railway.app/health
    hey -n 300 -c 10 https://be-api-production-4f32.up.railway.app/groups/1

### Test Configuration for health endpoint:

- Total requests: 1000
- Concurrent clients: 25
- Target endpoint: https://be-api-production-4f32.up.railway.app/health

### Results summary:

- Requests per second: approximately 443 requests per second
- Average latency: approximately 54 milliseconds
- Fastest response time: approximately 28 milliseconds
- Slowest response time: approximately 459 milliseconds
- Success rate: 100 percent (all responses returned HTTP 200)
### Latency distribution:

- 50 percent of requests completed in approximately 39 milliseconds
- 75 percent completed in approximately 46 milliseconds
- 90 percent completed in approximately 105 milliseconds
- 99 percent completed in approximately 457 milliseconds

### Interpretation:

The backend API remained fully responsive under concurrent load with no failed requests.

Average response times stayed well below 100 milliseconds, and higher latencies occurred only for a very small fraction of requests.

These results demonstrate that the deployed application performs reliably under moderate traffic and satisfies the performance requirements of this milestone.

---

## Deployment Verification

The correct operation of the deployed services can be verified using the following commands:

    curl https://be-api-production-4f32.up.railway.app/health
    curl https://be-api-production-4f32.up.railway.app/version
    curl https://fe-app-production-0d60.up.railway.app/api/health

### Manual verification via UI

- Create a new group  
- Add an expense  
- View balances and settlement suggestions  

All core features work correctly in the deployed environment.

---

## Conclusion

This milestone successfully delivers a complete cloud deployment of the ExpenseTracker application with:

- Automated deployments from GitHub  
- Persistent database storage  
- Real-time observability  
- Performance validation  

The application is fully operational, production-ready, and fulfills all requirements of **Hito 5**.
