#-----
# Base
#-----
FROM python:3.10.1-slim-bullseye as base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    VENV_PATH="/app/.venv"

ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

WORKDIR /app

#-----
# Deps
# Contains a virtual environment with all dependencies necessary
# to run the service.
#-----
FROM base as deps

RUN apt-get update \
    && apt-get install --no-install-recommends -y \
        curl \
        build-essential

# Install Poetry
RUN pip install 'poetry==1.1.12'

# Copy using poetry.lock* in case it doesn't exist yet
COPY ./pyproject.toml ./poetry.lock* /app/

RUN poetry update
RUN poetry install --no-root --no-dev

#-----
# Dev
# Contains service source and development dependencies.
# Can be used to run tests.
#-----
FROM deps as dev

RUN poetry install

COPY main.py /app
COPY ./client /app/client
COPY ./tests /app/tests
COPY ./resources /app/resources

# Run Tests
RUN poetry run pytest --full-trace


#-----
# Prod
# Minimal image with everything needed to run the service.
#-----
FROM base as prod

COPY --from=deps $VENV_PATH $VENV_PATH
COPY --from=dev /app/main.py /app/main.py
COPY --from=dev /app/client /app/client
COPY --from=dev /app/resources /app/resources

CMD [ "python", "main.py" ]
