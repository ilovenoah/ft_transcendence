FROM    debian:bullseye-slim

RUN     apt -y update
RUN     apt -y install redis-server

RUN     apt clean
RUN     rm -rf /var/lib/apt/lists/

COPY    ./conf/redis.conf /etc/redis/redis.conf

EXPOSE  6379

CMD ["redis-server", "--protected-mode no"]
#CMD [ "redis-server", "--protected-mode no", "/etc/redis/redis.conf" ]