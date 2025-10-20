# Hito 2: Continuous Integration

Student: Niklas Schuerrle  
Email: niklas733@correo.ugr.es  
Project: ExpenseTracker

---

## CI Status

![CI](https://github.com/niklas3739/ExpenseTracker/actions/workflows/ci.yml/badge.svg)

---

## Overview Milestone 2

The main goal of this milestone is to guarantee that the code is automatically tested before any deployment or integration.  
This ensures:
- Code quality and correctness through automated tests.  
- Easier collaboration and integration in agile workflows.  
- A reproducible, automated setup for both local and remote testing.

## Choice and configuration of the task manager
For this project, the chosen task manager is Makefile, a simple and powerful automation tool commonly used in software 
projects to define and execute development tasks consistently.  
`make` allows all contributors and the CI environment to run the same commands for installing dependencies, 
running tests, document testing coverage, and managing the project lifecycle.

`make` was chosen because it is lightweight and available by default on most systems.
It also ensures consistency between local development and continuous integration (e.g. via GitHub Actions).
Integrates easily with CI pipelines, allowing automated test runs after each push or pull request.
This setup ensures that running and verifying the project is fast, reproducible, and standardized across all environments.

[implemented Makefile here](../Makefile) 

---

## Choice and use of the assertion library

The project uses the assertion style provided by pytest, which extends Python’s built-in `assert` statements 
to offer clear, expressive, and automatically detailed error messages.  
This approach aligns with the principles of 
Test-Driven Development (TDD), allowing tests to remain simple, readable, and closely integrated with the language 
itself. The pytest assertions require no additional dependencies, provide introspection for failed tests, 
and work seamlessly with asynchronous code and coverage tools. This makes them an ideal choice for maintaining a 
lightweight and powerful testing workflow within the FastAPI-based project.

---

## Choice and use of the testing framework

The project uses **pytest** as the main testing framework due to its simplicity, flexibility, and extensive plugins. 
Pytest automatically discovers tests, manages fixtures, and provides powerful features. It is particularly suitable for 
FastAPI applications because it integrates seamlessly with 
asynchronous testing through `pytest-asyncio` and with HTTP client testing using `httpx`. Additionally, with pytest it's easy to make a test coverage analysis by using `pytest-cov`. 
Its strong community support and due to its ease of integration with continuous integration tools 
like GitHub Actions, this should be a good choice for this project.

---

## Continuous integration working and correct justification of the chosen system

For continuous integration, GitHub Actions is used for this project, because it's a free and fully integrated CI system 
provided by GitHub. It automatically runs the defined test suite and checks the project’s quality every time code is 
pushed or a pull request is opened. This ensures that all changes maintain the project’s stability. The workflow, 
defined in `.github/workflows/ci.yml`, installs dependencies, runs linting and type checks, and executes the tests using
the same commands defined in the Makefile. By that, consistency between local development and remote verification, can be 
guaranteed. GitHub Actions was also chosen because it offers good integration with GitHub repositories, automatic 
triggering of workflows on commits and pull requests, and easy configuration through YAML files. It also provides good 
support for dependency caching, service containers, and multiple Python versions. This setup ensures that testing, 
coverage, and validation processes are reproducible, fast, and reliable across all environments.

[find YAML file for Continous integration here](../.github/workflows/ci.yml)

---

## Implementation and execution of tests

The project includes a series of automated tests designed to verify basic functionality of the expense tracker application is working as expected. 
These tests focus on validating the creation, retrieval, and management of expenses and categories, ensuring that calculations such as total and filtered sums are correct. 
The tests are implemented using pytest and executed through the Makefile with the commands `make test` and `make cov`, which also generate detailed coverage reports.  
By integrating these tests into the continuous integration pipeline, every code change is automatically validated before merging and this prevents regressions and maintaining reliability. 
This setup ensures that both local development and CI environments execute the same testing process and this is contributing to a consistent and maintainable workflow.

---

## Screenshots
- [Test execution via CI](screenshots/ci_tests.png)