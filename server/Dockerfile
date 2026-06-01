FROM python:3.12-slim

WORKDIR /app

RUN pip install uv

COPY pyproject.toml uv.lock README.md ./
COPY src ./src

RUN uv sync --no-dev --frozen

ENV STORAGE_PATH=/data/uploads
RUN mkdir -p /data/uploads

EXPOSE 8787

CMD ["uv", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8787"]
