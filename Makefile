.PHONY: install test cov run lint format clean
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
