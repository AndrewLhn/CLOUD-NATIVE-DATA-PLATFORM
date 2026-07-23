COMPOSE := docker compose

.PHONY: up down logs build validate lint dbt-build dbt-compile dbt-test

up:
	$(COMPOSE) up -d --build

down:
	$(COMPOSE) down

logs:
	$(COMPOSE) logs -f

build:
	$(COMPOSE) build

validate:
	$(COMPOSE) config --quiet
	python3 -m compileall -q dags infra

lint:
	ruff check dags infra

dbt-build:
	$(COMPOSE) --profile tools run --rm dbt build

dbt-compile:
	$(COMPOSE) --profile tools run --rm dbt compile

dbt-test:
	$(COMPOSE) --profile tools run --rm dbt test
