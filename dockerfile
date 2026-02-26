FROM ghcr.io/astral-sh/uv:python3.14-alpine


WORKDIR /app

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project

COPY --exclude=docker* . /app

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked  

RUN apt-get update -y && apt-get install -y chromium

RUN echo 'export CHROMIUM_FLAGS="$CHROMIUM_FLAGS --no-sandbox"' >> /etc/chromium.d/default-flags


CMD [ "uv", "run", "bot.py" ]