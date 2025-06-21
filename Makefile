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
	sudo docker compose -f docker-compose.prod.yml up -d

docker-build-prod:
	sudo docker compose -f docker-compose.prod.yml up -d --build

docker-down-prod:
	sudo docker compose -f docker-compose.prod.yml down --rmi all

docker-down-prod-v:
	sudo docker compose -f docker-compose.prod.yml down --volumes --rmi all

docker-restart-prod:
	sudo docker compose -f docker-compose.prod.yml restart

docker-restart-api-prod:
	sudo docker compose -f docker-compose.prod.yml restart api

refresh-db:
	rm -rf db/data
