FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl build-essential \
    && rm -rf /var/lib/apt/lists/*

# requirements.txt lives at repo root (context = .)
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip \
    && pip install -r /app/requirements.txt

# Copy only your app package into the image (avoid copying the whole repo)
# Adjust this path if your Python package/module layout differs.
COPY expense_tracker /app/expense_tracker

EXPOSE 8000
CMD ["uvicorn", "expense_tracker.app:app", "--host", "0.0.0.0", "--port", "8000"]
