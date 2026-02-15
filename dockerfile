FROM ghcr.io/astral-sh/uv:python3.13-alpine

COPY --exclude=docker* --exclude=database.env . /app

WORKDIR /app
RUN uv sync --locked

CMD [ "uv", "run", "main.py" ]