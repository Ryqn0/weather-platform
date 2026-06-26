FROM python:3.14-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml uv.lock /app

RUN uv sync --frozen

COPY . /app

CMD ["uv", "run", "main.py"]