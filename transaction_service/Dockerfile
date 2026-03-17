FROM python:3.11-slim
WORKDIR /app
COPY transaction_service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY common/ ./common/
COPY transaction_service/ ./transaction_service/
EXPOSE 8000
CMD ["uvicorn", "transaction_service.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
