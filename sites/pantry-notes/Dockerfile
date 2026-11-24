# Django site served by gunicorn on port 3107. Only the project code is copied;
# README.md and MANIFEST.md never reach the image.
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY manage.py .
COPY pantry ./pantry
COPY recipes ./recipes
EXPOSE 3107
# One worker: submitted recipes are kept in memory, so every request must reach the
# same process (the shopping list lives in a signed cookie and works with any worker).
CMD ["gunicorn", "--bind", "0.0.0.0:3107", "--workers", "1", "--threads", "4", "pantry.wsgi:application"]
