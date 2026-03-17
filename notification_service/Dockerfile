FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY common/ ./common/
COPY notification_service/ ./notification_service/
EXPOSE 8000
CMD ["uvicorn", "notification_service.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
