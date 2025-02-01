FROM python:3.13-slim 

WORKDIR /src
COPY . .

RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8000"]

# docker buildx build --platform linux/amd64 -t woo204/winection-api:0.0.1 --push .
# docker pull woo204/winection-api:0.0.1
# docker run -d --name woo -p 8000:8000 woo204/winection-api:0.0.1