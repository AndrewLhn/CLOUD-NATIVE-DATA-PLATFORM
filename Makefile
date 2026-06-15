init:
	cd infra && terraform init

up:
	docker-compose -f docker/docker-compose.yaml up -d

clean:
	docker-compose -f docker/docker-compose.yaml down -v

test-dbt:
	cd dbt && dbt test