DOCKER_COMPOSE_YML = ./srcs/docker-compose.yml

build:
	mkdir -p /home/teko/data_t/postgres
	mkdir -p /home/teko/data_t/python
	docker compose -f $(DOCKER_COMPOSE_YML) build

up: build
	docker compose -f $(DOCKER_COMPOSE_YML) up -d

stop:
	docker compose -f $(DOCKER_COMPOSE_YML) stop

down:
	docker compose -f $(DOCKER_COMPOSE_YML) down --rmi all

clean:
	rm -fr /home/tyonezaw/data
	docker compose -f $(DOCKER_COMPOSE_YML) down --rmi all -v --remove-orphans

allclean:
	rm -fr /home/tyonezaw/data_t
	docker compose -f $(DOCKER_COMPOSE_YML) down --rmi all -v --remove-orphans
	docker builder prune
	
re: down up

restart:
	docker compose -f $(DOCKER_COMPOSE_YML) restart
