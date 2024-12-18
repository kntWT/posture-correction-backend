docker-up-dev:
	docker compose -f docker-compose.dev.yml up -d

docker-build-dev:
	docker compose -f docker-compose.dev.yml up -d --build

docker-restart-dev:
	docker compose -f docker-compose.dev.yml restart

docker-restart-api-dev:
	docker compose -f docker-compose.dev.yml restart api

docker-down-dev:
	docker compose -f docker-compose.dev.yml down --rmi all

docker-down-dev-v:
	docker compose -f docker-compose.dev.yml down --volumes --rmi all

docker-up-prod:
	docker compose -f docker-compose.prod.yml up -d

docker-build-prod:
	docker compose -f docker-compose.prod.yml up -d --build

docker-down-prod:
	docker compose -f docker-compose.prod.yml down --rmi all

docker-down-prod-v:
	docker compose -f docker-compose.prod.yml down --volumes --rmi all

docker-restart-prod:
	docker compose -f docker-compose.prod.yml restart

docker-restart-api-prod:
	docker compose -f docker-compose.prod.yml restart api
