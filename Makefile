DOCKER_COMPOSE_YML = ./srcs/docker-compose.yml

build:
	docker compose -f $(DOCKER_COMPOSE_YML) build

up: build
	docker compose -f $(DOCKER_COMPOSE_YML) up -d
	docker exec -it django4242 python manage.py migrate
#	chmod -R 777 ./srcs/data/postgres

stop:
	docker compose -f $(DOCKER_COMPOSE_YML) stop

down:
	docker compose -f $(DOCKER_COMPOSE_YML) down --rmi all

pgclean: #postgresのvolumeを削除する
	docker compose -f $(DOCKER_COMPOSE_YML) down --rmi all --remove-orphans
	docker volume rm  srcs_postgres_data

clean: #すべてのvolumeを削除する
	docker compose -f $(DOCKER_COMPOSE_YML) down --rmi all -v --remove-orphans

allclean: #全部キレイにする buildするときのcacheも
	docker compose -f $(DOCKER_COMPOSE_YML) down --rmi all -v --remove-orphans
	docker builder prune
#	rm -fr ./src/data
	
re: down up

restart:
	docker compose -f $(DOCKER_COMPOSE_YML) restart
