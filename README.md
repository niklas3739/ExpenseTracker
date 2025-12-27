# ExpenseTracker

**Project**: Expense Tracker - Cloud-Based Personal Finance Application  
**Author**: Niklas Schuerrle  
**Email**: niklas733@correo.ugr.es  
**Course**: Cloud Computing - Fundamentos e Infraestructuras

--- 

## Overview
The **Expense Tracker** is a cloud-based web application designed to help users record, categorize, and analyze their daily expenses.  
It aims to provide insights into spending habits through summaries and visual reports — accessible anytime, anywhere, via the cloud.

---

## CI Status

![CI](https://github.com/niklas3739/ExpenseTracker/actions/workflows/ci.yml/badge.svg)

---

## Milestones

### Hito 1 – Repository Setup and Project Definition
Initial setup of the Git environment, repository structure, and project definition.  
Configured GitHub with SSH authentication and 2FA, created the project repository, and documented the architecture and goals of the ExpenseTracker application.

### Hito 2 – Continuous Integration
Implemented automated testing and continuous integration using **GitHub Actions** and **Makefile**.  
Configured **pytest** for test execution and coverage reporting to ensure code quality, reproducibility, and stable collaboration across environments.

### Hito 3 – Development of Microservices
Designed and implemented the backend as a **FastAPI microservice** with structured logging via **structlog**.  
Separated API, business, and persistence layers, added full testing for all routes and logic, and automated deployment verification through CI.

### **Hito 4 – Composition of Services**
Containerized the application and designed a complete **multi-service architecture** using Docker and Docker Compose.  
Created Docker images for the backend, frontend, and database, configured persistent storage through volumes, added an automated cluster health test, and published all microservice images to **GitHub Packages** using CI/CD workflows.

### **Hito 5 - Deployment of the Application on a PaaS**
Deployed the complete ExpenseTracker application to a **production-grade cloud environment** using the Railway PaaS.  
Configured automated deployments directly from GitHub, connected a managed PostgreSQL database, implemented real-time observability through logs and metrics, and validated the deployment with performance and stress testing to ensure reliability and scalability.

## Documentation
- [Milestone 1 – Repository Setup and Project Definition](docs/hito01.md)
- [Milestone 2 – Continuous Integration](docs/hito02.md)
- [Milestone 3 – Development of Microservices](docs/hito03.md)
- [Milestone 4 – Composition of Services](docs/hito04.md)
- [Milestone 5 – Deployment of the Application on a PaaS](docs/hito05.md)

