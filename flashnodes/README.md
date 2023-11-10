# flashnodes

## Backend Requirements

* [Docker](https://www.docker.com/).
* [Docker Compose](https://docs.docker.com/compose/install/).
* [Poetry](https://python-poetry.org/) for Python package and environment management.

## Backend local development

* Start the stack with Docker Compose:

```bash
docker-compose up -d
```

* Now you can open your browser and interact with these URLs:

Backend, JSON based web API based on OpenAPI: http://localhost:8080/api/

Automatic interactive documentation with Swagger UI (from the OpenAPI backend): http://localhost:8080/docs

Alternative automatic documentation with ReDoc (from the OpenAPI backend): http://localhost:8080/redoc

PGAdmin, PostgreSQL web administration: http://localhost:5050

Flower, administration of Celery tasks: http://localhost:5555

To check the logs, run:

```bash
docker-compose logs
```

To check the logs of a specific service, add the name of the service, e.g.:

```bash
docker-compose logs backend
```

If your Docker is not running in `localhost` (the URLs above wouldn't work) check the sections below on **Development with Docker Toolbox** and **Development with a custom IP**.

## Backend local development, additional details
...
