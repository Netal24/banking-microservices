FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY common/ ./common/
COPY account_service/ ./account_service/
EXPOSE 8000
CMD ["uvicorn", "account_service.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
