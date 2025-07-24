# ---------- Stage 1: Build Stage ----------
# This stage installs dependencies into wheels for a smaller final image.
FROM python:3.11-slim AS build
WORKDIR /app

# Install build dependencies
RUN pip install --no-cache-dir wheel

# Copy requirements and build wheels
COPY requirements.txt .
RUN pip wheel --no-cache-dir --wheel-dir=/wheels -r requirements.txt


# ---------- Stage 2: Runtime Stage ----------
# This is the final, lean image.
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Create a non-root user
RUN useradd -m -u 1001 manalytics
WORKDIR /app

# Copy pre-built wheels from the build stage and install them
COPY --from=build /wheels /wheels
RUN pip install --no-cache-dir /wheels/* && rm -rf /wheels

# Copy the application code
COPY . .

# Change ownership to the non-root user
RUN chown -R manalytics:manalytics /app

USER manalytics

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "src.api.app:app", "--host", "0.0.0.0", "--port", "8000"]