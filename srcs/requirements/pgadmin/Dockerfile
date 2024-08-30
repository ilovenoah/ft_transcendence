FROM    dpage/pgadmin4:latest

# From    debian:bullseye-slim

# RUN     apt update
# RUN     apt -y install gnupg gnupg2 curl
# RUN     echo "deb https://ftp.postgresql.org/pub/pgadmin/pgadmin4/apt/$(lsb_release -cs) pgadmin4 main" | tee /etc/apt/sources.list.d/pgadmin4.list
# RUN     curl https://www.pgadmin.org/static/packages_pgadmin_org.pub | apt-key add
# RUN     apt update
# RUN     apt -y install pgadmin4-web

# RUN     apt clean
# RUN     rm -rf /var/lib/apt/lists/



#WORKDIR /var/www/html

#COPY    ./conf/default.conf /etc/nginx/sites-available/default

EXPOSE  80

CMD ["tail",  "-f", "/dev/null"]
