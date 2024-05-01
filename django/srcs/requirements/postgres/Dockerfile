From    debian:bullseye-slim

RUN     apt -y update
RUN     apt install -y postgresql
RUN     apt install -y postgresql-contrib

RUN     apt clean
RUN     rm -rf /var/lib/apt/lists/

COPY    conf/postgresql.conf /etc/postgresql/postgresql.conf


EXPOSE 5432


RUN     mkdir -p /var/lib/postgresql/data
RUN     chown -R postgres:postgres /var/lib/postgresql/data
RUN     chmod -R 700 /var/lib/postgresql/data

# PostgreSQLを実行するための非特権ユーザーを作成
#RUN useradd --create-home --shell /bin/bash postgres_user

# PostgreSQLを非特権ユーザーで実行
USER postgres

#RUN     chown -R postgre:postgre /val/lib/postgre
CMD ["/usr/lib/postgresql/13/bin/postgres", "-D", "/var/lib/postgresql/data", "-c", "config_file=/etc/postgresql/postgresql.conf"]
