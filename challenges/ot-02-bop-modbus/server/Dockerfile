FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir pymodbus==3.6.8

COPY server.py .

EXPOSE 502

CMD ["python", "-u", "server.py"]
