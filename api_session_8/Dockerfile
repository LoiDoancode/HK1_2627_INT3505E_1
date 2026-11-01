# ==========================================
# Dockerfile Multi-stage chuẩn production (Slide 38)
# Tách biệt builder và runtime để tối ưu kích thước image và tăng cường bảo mật
# ==========================================

# ─── Stage 1: Builder ───
FROM python:3.11-slim AS builder

WORKDIR /build

# Cài đặt công cụ build cần thiết cho thư viện C (psycopg2)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# ─── Stage 2: Runtime ───
FROM python:3.11-slim AS runtime

WORKDIR /app

# Cài đặt runtime dependency cho PostgreSQL
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Tạo non-root user 'app' (Bảo mật 12-factor)
RUN groupadd -r app && useradd -r -g app -d /app app

# Copy virtualenv từ builder
COPY --from=builder /opt/venv /opt/venv

# Copy toàn bộ source code
COPY --chown=app:app . /app

ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

USER app

EXPOSE 5000

# Chạy bằng Gunicorn WSGI Server (Slide 37)
CMD ["gunicorn", "-c", "gunicorn.conf.py", "wsgi:app"]

