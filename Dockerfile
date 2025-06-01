FROM python:3.12-alpine

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt && rm /tmp/requirements.txt

COPY vpn2config .

CMD ["waitress-serve", "--listen=0.0.0.0:8000", "app:app"]