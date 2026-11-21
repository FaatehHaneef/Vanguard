# Vanguard backend (API) without a browser. Dockerfile.worker adds Playwright and Chromium.
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app

COPY pyproject.toml ./
COPY vanguard ./vanguard
RUN pip install --no-cache-dir .

EXPOSE 8000
CMD ["uvicorn", "vanguard.api:app", "--host", "0.0.0.0", "--port", "8000"]
