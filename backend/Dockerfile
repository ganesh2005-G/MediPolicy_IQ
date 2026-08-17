# ==========================================
# Multi-Stage Build optimized for MediPolicy_IQ
# ==========================================

# --- Stage 1: Build & Dependency compilation ---
FROM python:3.12-slim AS builder

WORKDIR /build

# Install compilation toolchain & Postgres dev libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Install dependencies in a wheels cache
RUN pip install --no-cache-dir --user -r requirements.txt

# --- Stage 2: Final Light Container ---
FROM python:3.12-slim AS runner

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy python packages compiled from the builder stage
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Copy app code
COPY app /app/app

# Expose server port
EXPOSE 8000

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
