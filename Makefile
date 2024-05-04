DOCKER_COMPOSE_YML = ./srcs/docker-compose.yml

build:
	docker compose -f $(DOCKER_COMPOSE_YML) build

up: build
	docker compose -f $(DOCKER_COMPOSE_YML) up -d
	chmod -R 777 ./src/data/postgres

stop:
	docker compose -f $(DOCKER_COMPOSE_YML) stop

down:
	docker compose -f $(DOCKER_COMPOSE_YML) down --rmi all

clean:
	docker compose -f $(DOCKER_COMPOSE_YML) down --rmi all -v --remove-orphans
#	rm -fr ./src/data

allclean:
	docker compose -f $(DOCKER_COMPOSE_YML) down --rmi all -v --remove-orphans
	docker builder prune
#	rm -fr ./src/data
	
re: down up

restart:
	docker compose -f $(DOCKER_COMPOSE_YML) restart
