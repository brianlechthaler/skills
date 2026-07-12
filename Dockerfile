FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml install.py ./
COPY scripts/ scripts/
COPY tests/ tests/

RUN pip install --no-cache-dir pytest pytest-cov ruff

CMD ["pytest", "--cov=install", "--cov-report=term-missing", "--cov-fail-under=100", "-v"]
