From    debian:bullseye-slim

RUN     apt -y update
RUN     apt install -y mariadb-server
RUN     apt install -y zip

RUN     apt clean
RUN     rm -rf /var/lib/apt/lists/

COPY    ./conf/50-server.cnf /etc/mysql/mariadb.conf.d/

RUN     mkdir -p /var/lib/mysql
WORKDIR /var/lib/mysql

COPY    ./utils/wordpresssql.zip /wordpresssql.zip 

COPY    ./utils/setup.sh /setup.sh
RUN     chmod +x /setup.sh

EXPOSE 3306

CMD ["/setup.sh"]

