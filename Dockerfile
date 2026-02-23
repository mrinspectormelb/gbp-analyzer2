FROM mcr.microsoft.com/playwright/python:v1.46.0-jammy

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port $PORT --workers 1"]
