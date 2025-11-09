# Multi-stage Dockerfile for Board Game Tracker
# Optimized for ARM64 (Raspberry Pi 5)

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ ./backend/

# Copy frontend code
COPY frontend/ ./frontend/

# Create directory for SQLite database
RUN mkdir -p /app/data

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV SQLALCHEMY_DATABASE_URL=sqlite:///./data/boardgames.db

# Expose port
EXPOSE 8000

# Run the application with uvicorn serving both API and static files
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
