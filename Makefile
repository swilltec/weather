bash:
	@docker exec -it weather_api bash

build:
	@docker compose build

down:
	@docker compose down

format:
	@docker exec -it weather_api isort --profile black .
	@docker exec -it weather_api ruff format .
	@docker exec -it weather_api ruff check . --fix --select I001

lint:
	@docker exec -it weather_api ruff check .

migrate:
	@docker exec -it weather_api python backend/manage.py migrate

migrations:
	@docker exec -it weather_api python backend/manage.py makemigrations

resetdb:
	@docker exec -it weather_api python backend/manage.py reset_db --noinput



shell:
	@docker exec -it weather_api python backend/manage.py shell

stop:
	@docker compose stop

up:
	@docker compose up
