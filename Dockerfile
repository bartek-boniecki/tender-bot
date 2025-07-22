FROM python:3.11-slim

WORKDIR /app
COPY . .

# Install Playwright system dependencies for Chromium/Firefox/Webkit
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ca-certificates \
    fonts-liberation \
    libappindicator3-1 \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libc6 \
    libcairo2 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libexpat1 \
    libgbm1 \
    libgcc1 \
    libglib2.0-0 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libpango-1.0-0 \
    libu2f-udev \
    libwayland-client0 \
    libwayland-cursor0 \
    libwayland-egl1 \
    libx11-6 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxi6 \
    libxrandr2 \
    libxrender1 \
    libxkbcommon0 \
    libxshmfence1 \
    xdg-utils \
    wget \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers
RUN python -m playwright install --with-deps

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
