FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9

WORKDIR /app

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

ENV PATH="${PATH}:/root/.local/bin"

RUN poetry config virtualenvs.create false

# Copy poetry.lock* in case it doesn't exist in the repo
COPY ./pyproject.toml ./app/poetry.lock* /

# Allow installing dev dependencies to run tests
ARG INSTALL_DEV=false
RUN bash -c "if [ $INSTALL_DEV == 'true' ] ; then poetry install --no-root ; else poetry install --no-root --only main; fi"

COPY ./ /app
#COPY ./alembic /alembic
ENV PYTHONPATH=/app
