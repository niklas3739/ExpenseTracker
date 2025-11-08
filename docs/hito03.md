# Hito 3: Development of Microservices

Student: Niklas Schuerrle  
Email: niklas733@correo.ugr.es  
Project: ExpenseTracker

---

## CI Status

![CI](https://github.com/niklas3739/ExpenseTracker/actions/workflows/ci.yml/badge.svg)

---

## Overview Milestone 3

The main goal of this milestone is to design and implement a **microservice** based on the functionality developed in previous milestones.  
This includes exposing the application’s functionality through a RESTful API, adding structured logging, testing the API comprehensively, and providing the infrastructure to run and test the microservice independently.

The outcome is a fully functional **backend microservice** for managing group expenses, members, balances, and settlements which are accessible through HTTP routes, well-tested, and ready for integration with other potential services.

---

## Choice and justification of the microservice framework

The chosen framework for this milestone is **FastAPI**.  
FastAPI is a simple, modern and high-performance Python web framework ideal for creating **microservices and APIs**.  

**Reasons for choosing FastAPI:**
- **Automatic data validation and serialization** using Pydantic models.  
- **Dependency injection system**, allowing clean separation between database logic, business logic, and API routes.  
- **Automatic interactive documentation** with for example Swagger UI.  
- **Great testing support** via `pytest` and `httpx`.  

---

## Design and separation of API and business logic

The ExpenseTracker backend is built following a **layered architecture**, for having modularity and separation.

**Architecture overview:**
- **API layer** (`expense_tracker/api/routes/`):  
  Contains all REST endpoints (groups, expenses, settlements, balances).  
  Handles input validation, error translation, and route organization.

- **Business logic layer** (`expense_tracker/services/`):  
  Contains reusable core logic, such as balance computation, expense splitting, and settlement handling.  
  This logic is independent of the web framework and can be tested in isolation.

- **Persistence layer** (`expense_tracker/core/db.py`):  
  Manages database initialization and sessions using dependency injection (`get_db`).  
  The database engine uses `SQLModel` for table definitions and schema management.

This structure ensures a clean microservice design with a reusable business logic.

---

## Use and justification of the logging system

To monitor and trace system behavior, a **structured logging system** was added using the **structlog** library.  
This allows the API to record every important event in a structured, machine-readable format (JSON).

**Example log entries:**
```json
[
  {"event": "group_created", "group_id": 1, "name": "Trip", "members": 3, "level": "info"},
  {"event": "expense_added", "group_id": 1, "amount": 60.0, "payer": "alice", "split_type": "equal", "level": "info"}
]
```
**Reasons for using structlog:**
- Provides structured, contextual logs for easier analysis.
- Integrates seamlessly with FastAPI.
- Supports output in JSON for use in log aggregation systems.
- Helps debug API requests and monitor service activity.
- Structured logs are crucial for scalable microservices, as they allow easy monitoring across distributed systems.

---

## Use and justification of the logging system

The project uses a **Makefile** to automate development and testing tasks, ensuring consistency across environments.  
It defines common commands for installing dependencies, running tests, generating coverage reports, and starting the application.

**Main Makefile tasks:**
- `make install` → install all project dependencies  
- `make run` → start the API locally using **Uvicorn**  
- `make test` → run all automated tests using **pytest**  
- `make cov` → execute tests with coverage reporting (fails if coverage < 85 %)  
- `make clean` → remove caches, build artifacts, and coverage reports  

[See the Makefile here](../Makefile)

This setup guarantees that the build, test, and deployment processes are **reproducible and automated** across both local and continuous integration environments.  
It also ensures that CI (via GitHub Actions) runs exactly the same commands that developers use locally, achieving full consistency between environments.

## Testing of the API and Business Logic

The tests have been implemented using **pytest** to ensure that all components of the microservice behave as expected and 
the tests cover both the **API layer** and the **business logic layer**, verifying that routes, validations, and calculations work correctly.
And all tests run against an in-memory SQLite database, created dynamically for each session.

**Main tested components:**
- **Groups:** creation and retrieval of groups and their members.  
- **Expenses:** adding expenses using different split types (“equal”, “shares”, and “percent”).  
- **Settlements:** registering payments between users.  
- **Balances:** computing balances and generating payout suggestions.

Tests can be executed locally using:
```bash
make test
```
or with coverage reporting:
```bash
make cov
```

All tests are also executed automatically by GitHub Actions in the CI workflow on every push or pull request.
This ensures that the service remains stable and all functionality is verified before merging new code.

## Continuous integration and automation

Continuous Integration (CI) is implemented using **GitHub Actions**, which automatically validates every change pushed to the repository.  
This ensures that the project remains stable, tested, and deployable at all times.

The workflow defined in `.github/workflows/ci.yml` runs automatically on each **commit** or **pull request** and performs the following steps:

1. **Setup environment:** install Python and project dependencies.  
2. **Linting and static analysis:** verify code quality and style.  
3. **Run tests:** execute all automated tests using `pytest`.  
4. **Coverage analysis:** ensure the minimum coverage threshold (85 %) is met.  

[Find the CI configuration here](../.github/workflows/ci.yml)

## 