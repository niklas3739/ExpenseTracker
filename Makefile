.PHONY: install test run clean dev

# Install runtime (+ dev) deps
install:
	python -m pip install --upgrade pip
	pip install -r requirements.txt

dev:
	python -m pip install --upgrade pip
	pip install -r requirements.txt -r requirements-dev.txt

# Run the test suite
test:
	python -m pytest -q

# Run the API locally with reload (your app is in src/expense_tracker/app.py)
run:
	uvicorn expense_tracker.app:app --reload --app-dir src

# Clean caches
clean:
	rm -rf __pycache__ .pytest_cache *.pyc

