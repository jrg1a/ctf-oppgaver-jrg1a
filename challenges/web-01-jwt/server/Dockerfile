FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir flask==3.0.3 PyJWT==2.9.0

COPY app.py .
COPY templates/ templates/

EXPOSE 5000

CMD ["python", "app.py"]
