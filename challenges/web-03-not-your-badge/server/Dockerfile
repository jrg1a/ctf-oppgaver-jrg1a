FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN pip install --no-cache-dir flask==3.0.3

COPY app.py .

RUN useradd --create-home --shell /usr/sbin/nologin ctf
USER ctf

EXPOSE 5000

CMD ["python", "app.py"]
