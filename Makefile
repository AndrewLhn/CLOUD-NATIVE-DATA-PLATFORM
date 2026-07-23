COMPOSE := docker compose

.PHONY: up down logs build validate lint

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
