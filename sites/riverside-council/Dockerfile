# Flask site served by gunicorn. Only app.py, templates/ and static/ are copied;
# README and MANIFEST stay out of the image.
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
COPY templates/ templates/
COPY static/ static/
EXPOSE 3103
# One worker: reports are kept in memory, so every request must reach the same process.
CMD ["gunicorn", "--bind", "0.0.0.0:3103", "--workers", "1", "--threads", "4", "app:app"]
