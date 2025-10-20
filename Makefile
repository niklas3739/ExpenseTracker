.PHONY: install dev test run cov clean

PY := python
PIP := pip

install:
	$(PY) -m pip install --upgrade pip
	$(PIP) install -r requirements.txt

# Run the test suite
test:
	$(PY) -m pytest -q

cov:
	$(PY) -m pytest --cov=expense_tracker --cov-report=term-missing --cov-report=html --cov-fail-under=85

# Run the API locally with reload
run:
	uvicorn expense_tracker.app:app --reload

# Clean caches/build artifacts
clean:
	rm -rf __pycache__ .pytest_cache .mypy_cache
	rm -rf .coverage htmlcov
	rm -rf build dist *.egg-info
	find . -name "*.pyc" -delete -o -name "*.pyo" -delete
