FROM python:3.10-slim
WORKDIR /app
RUN pip install --no-cache-dir flask==3.0.2 werkzeug==3.0.1 gunicorn==21.2.0
COPY app.py .
EXPOSE 5000
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:5000", "app:app"]
