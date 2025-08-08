FROM python:3.11-slim

# System deps for Playwright
RUN apt-get update && \
    apt-get install -y curl gnupg ca-certificates libnss3 libatk1.0-0 libatk-bridge2.0-0 \
      libcups2 libxkbcommon0 libxcomposite1 libxdamage1 libxrandr2 libgbm1 libasound2 \
      libpangocairo-1.0-0 libgtk-3-0 libdrm2 && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Python deps
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Playwright browsers
RUN playwright install --with-deps

COPY . .

# Bind to Railway’s port (or default to 8000)
CMD exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
