.PHONY: help up down etl clean logs status

# Default target
help:
	@echo "=========================================="
	@echo "Sales ETL Project - Available Commands"
	@echo "=========================================="
	@echo "  make up      - Start PostgreSQL container"
	@echo "  make down    - Stop PostgreSQL container"
	@echo "  make etl     - Run the ETL pipeline"
	@echo "  make clean   - Stop containers and remove volumes"
	@echo "  make logs    - Show PostgreSQL logs"
	@echo "  make status  - Check container status"
	@echo "=========================================="

# Start PostgreSQL container
up:
	@echo "Starting PostgreSQL container..."
	docker compose up -d
	@echo "Waiting for PostgreSQL to be ready..."
	@sleep 5
	@echo "PostgreSQL is ready!"
	@docker compose ps

# Stop PostgreSQL container
down:
	@echo "Stopping PostgreSQL container..."
	docker compose down

# Run ETL pipeline
etl:
	@echo "Running ETL pipeline..."
	@if [ ! -f .env ]; then \
		echo "Creating .env file from .env.example..."; \
		cp .env.example .env; \
	fi
	python3 etl/run_pipeline.py

# Clean up everything (stop containers and remove volumes)
clean:
	@echo "Cleaning up containers and volumes..."
	docker compose down -v
	@echo "Cleanup complete!"

# Show PostgreSQL logs
logs:
	docker compose logs -f postgres

# Check container status
status:
	@echo "Container status:"
	@docker compose ps
