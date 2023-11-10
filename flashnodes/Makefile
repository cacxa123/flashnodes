migrate-init:
	docker-compose run backend alembic revision --autogenerate -m "migration"

migrate:
	docker-compose run backend alembic upgrade head

isort:
	isort . --skip alembic --skip venv