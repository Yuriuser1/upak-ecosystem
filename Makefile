# UPAK Ecosystem Makefile

.PHONY: help install test test-verbose lint format run run-dev build docker-build docker-run clean

help:
	@echo "Available commands:"
	@echo "  install      - Install dependencies"
	@echo "  test         - Run tests"
	@echo "  test-verbose - Run tests with verbose output"
	@echo "  lint         - Run linting"
	@echo "  format       - Format code"
	@echo "  run          - Run application in production mode"
	@echo "  run-dev      - Run application in development mode"
	@echo "  build        - Build application"
	@echo "  docker-build - Build Docker image"
	@echo "  docker-run   - Run Docker container"
	@echo "  clean        - Clean temporary files"

install:
	pip install -r requirements.txt

test:
	pytest tests/ -v

test-verbose:
	pytest tests/ -v -s

lint:
	flake8 app.py tests/

format:
	black app.py tests/

run:
	gunicorn --bind 0.0.0.0:5000 --workers 4 app:app

run-dev:
	FLASK_ENV=development python app.py

build:
	@echo "Building UPAK Ecosystem..."
	python -m py_compile app.py
	@echo "Build completed successfully"

docker-build:
	docker build -t upak-ecosystem .

docker-run:
	docker-compose up -d

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf .pytest_cache/
	rm -rf logs/*.log
