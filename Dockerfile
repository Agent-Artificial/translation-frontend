FROM python:3.12.4-slim-bookworm

ARG dev

ENV dev=${dev} \
  PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  # Poetry's configuration:
  POETRY_NO_INTERACTION=1 \
  POETRY_VIRTUALENVS_CREATE=false \
  POETRY_CACHE_DIR='/var/cache/pypoetry' \
  POETRY_HOME='/usr/local' \
  POETRY_VERSION=1.8.3
  # ^^^
  # Make sure to update it!

# System deps:
RUN apt-get update && apt-get install -y curl ffmpeg
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH=~/.local/share/pypoetry/venv/bin/poetry:$PATH

# Copy only requirements to cache them in docker layer
WORKDIR /app
COPY poetry.lock pyproject.toml /app/

RUN echo $(ls -lash)
RUN echo $(ls -lash /app)

# Project initialization:
RUN poetry install --no-interaction --no-ansi

# Creating folders, and files for a project:
COPY . /app

CMD ["poetry", "run", "uvicorn", "frontend.main:app", "--host", "0.0.0.0", "--port", "8000"]