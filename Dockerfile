# Use a lightweight Python image
FROM python:3.12-slim

# Prevent Python from buffering stdout/stderr
ENV PYTHONUNBUFFERED=1

# Cloud Run expects $PORT
ENV PORT=8080

# Set working directory
WORKDIR /app

# Install uv tool globally
RUN pip install --no-cache-dir --upgrade pip uv>=0.7.19

# Copy only dependency files first for Docker caching
COPY ai_agent ./ai_agent
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen

# Copy the rest of the application code and tools config
COPY . .
COPY toolbox-alloydb-local.yaml /app/toolbox-alloydb-local.yaml

# Expose the port (Cloud Run will use $PORT)
EXPOSE 8080

# Start the toolbox server using the tools config
# Cloud Run sets $PORT automatically
CMD ["uv", "run", "uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8080"]