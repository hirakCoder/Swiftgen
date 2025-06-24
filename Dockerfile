# Multi-stage build for SwiftGen
FROM python:3.11-slim as builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY backend/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --user -r requirements.txt

# Production stage
FROM python:3.11-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 swiftgen

# Copy Python dependencies from builder
COPY --from=builder /root/.local /home/swiftgen/.local

# Set working directory
WORKDIR /app

# Copy application code
COPY backend/ ./backend/
COPY frontend/ ./frontend/
COPY templates/ ./templates/
COPY run_tests.py pytest.ini ./

# Create necessary directories
RUN mkdir -p workspaces logs && \
    chown -R swiftgen:swiftgen /app

# Switch to non-root user
USER swiftgen

# Add local bin to PATH
ENV PATH=/home/swiftgen/.local/bin:$PATH

# Expose port
EXPOSE 8002

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8002/health || exit 1

# Run the application
CMD ["python", "backend/main.py"]