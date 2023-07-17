FROM python:3.11-slim-bookworm as base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    # prevents python creating .pyc files
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    # pysetup
    PYSETUP_PATH="/opt/pysetup" \
    VENV_PATH="/opt/pysetup/.venv"

ENV PATH="${POETRY_HOME}/bin:${VENV_PATH}/bin:${PATH}"

FROM base as builder

RUN apt-get update && \
    apt-get install -y curl \
    && rm -rf /var/lib/apt/lists/*

# install poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

WORKDIR ${PYSETUP_PATH}

COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root

# production container
FROM base as production
ENV FASTAPI_ENV=production
COPY --from=builder ${PYSETUP_PATH} ${PYSETUP_PATH}
COPY ./test_slack_app/ /app
WORKDIR /app

HEALTHCHECK CMD curl http://localhost:8000/ping || exit 1

# run app with gunicorn + uvicorn
CMD ["gunicorn", "-w", "1", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000","main:fastapi_app"]
