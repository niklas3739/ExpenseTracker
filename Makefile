.PHONY: install test cov run lint format clean \
        fe-install fe-build fe-test fe-clean \
        up down logs ps rebuild clean-all test-compose

PY := python
PIP := pip

install:
	$(PY) -m pip install --upgrade pip
	$(PIP) install -r requirements.txt

test:
	$(PY) -m pytest -q tests

cov:
	$(PY) -m pytest --cov=expense_tracker --cov-report=term-missing --cov-fail-under=85

format:
	$(PY) -m black expense_tracker tests

run:
	uvicorn expense_tracker.app:app --reload --host 0.0.0.0 --port 8000

clean:
	rm -rf __pycache__ .pytest_cache .mypy_cache .coverage htmlcov build dist *.egg-info
	find . -name "*.py[co]" -delete

lint:
	$(PY) -m flake8 expense_tracker tests

# Frontend
fe-install:
	cd frontend && npm ci --no-audit --no-fund

fe-build:
	cd frontend && npm run build

fe-test:
	cd frontend && npm test -- --watchAll=false

fe-clean:
	rm -rf frontend/node_modules frontend/build

# Docker Compose
up:
	docker compose up -d --build

down:
	docker compose down

logs:
	docker compose logs -f --tail=100

ps:
	docker compose ps

rebuild:
	docker compose build --no-cache

clean-all:
	docker compose down -v
	docker system prune -f

# Required cluster test
test-compose:
	docker compose up -d --build
	# Give services time to initialize
	sleep 10
	curl -f http://localhost:8000/health || (echo "API health check FAILED" && docker compose logs api && exit 1)
	docker compose down
