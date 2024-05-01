From    debian:bullseye-slim

RUN     apt -y update
RUN     apt install -y python3
RUN     apt install -y fcgiwrap
RUN     apt install -y pip

RUN     apt clean
RUN     rm -rf /var/lib/apt/lists/

RUN     mkdir -p /var/www/html
WORKDIR /var/www/html

COPY    ./utils/index.py /var/www/html/index.py
RUN     chmod 755 index.py

EXPOSE  9000
CMD ["fcgiwrap", "-c", "4", "-s", "tcp:0.0.0.0:9000"]

