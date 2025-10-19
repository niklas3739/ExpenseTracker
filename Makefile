.PHONY: test run install clean

# Install runtime + test deps from requirements.txt
install:
	python -m pip install --upgrade pip
	pip install -r requirements.txt

# Run the test suite with pytest
test:
	pytest -q

# Run the API locally with reload
run:
	uvicorn expense_tracker.main:app --reload --app-dir src

# Remove caches and temporary files
clean:
	rm -rf __pycache__ .pytest_cache *.pyc
