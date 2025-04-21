FROM python:3.13-slim AS builder

WORKDIR /app
COPY ./requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

FROM python:3.13-slim

WORKDIR /app

# Kopiuj całą zawartość swift-api
COPY swift-api .

# Kopiuj zainstalowane zależności
COPY --from=builder /root/.local /root/.local

# Ustaw zmienne środowiskowe
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONPATH=/app
ENV DB_HOST=db
ENV DB_USER=postgres
ENV DB_PASSWORD=postgres
ENV DB_NAME=swiftdb

# Ustaw prawa wykonania dla skryptów
RUN find /app/app/scripts -name "*.py" -exec chmod +x {} \;

EXPOSE 8080

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]