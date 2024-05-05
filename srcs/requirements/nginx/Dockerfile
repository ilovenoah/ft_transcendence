From    debian:bullseye-slim

RUN     apt -y update
RUN     apt install -y nginx 
RUN     apt install -y openssl
RUN     apt install -y curl

RUN     apt clean
RUN     rm -rf /var/lib/apt/lists/

RUN     mkdir -p /etc/nginx/ssl
RUN     openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
            -keyout /etc/nginx/ssl/ssl-cert.key \
            -out /etc/nginx/ssl/ssl-cert.crt \
            -subj "/C=JP/ST=TOKYO/L=SHINJUKU/O=42Tokyo/CN=tyonezaw.42.fr"

RUN     mkdir -p /var/www/html
WORKDIR /var/www/html

COPY    ./conf/default.conf /etc/nginx/sites-available/default

EXPOSE  443
EXPOSE  8080

CMD     ["nginx", "-g", "daemon off;"]
