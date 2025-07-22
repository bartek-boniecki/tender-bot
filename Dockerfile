FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers (needed for scraping)
RUN python -m playwright install

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
