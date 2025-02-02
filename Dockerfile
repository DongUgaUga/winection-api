FROM --platform=linux/amd64 python:3.9-slim-buster

WORKDIR /src

COPY requirements.txt .
RUN apt update && apt install -y libpq-dev gcc && \
    pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--reload-dir", "src"]
