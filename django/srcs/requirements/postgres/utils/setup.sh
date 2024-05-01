#!/bin/bash


# PostgreSQLをバックグラウンドで起動
service postgresql start


#echo "CREATE DATABASE wordpress DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;" > /init.sql
#echo "CREATE USER 'wordpressuser'@'%' IDENTIFIED BY 'password';" >> /init.sql
#echo "GRANT ALL PRIVILEGES ON wordpress.* TO 'wordpressuser'@'%';" >> /init.sql
#echo "FLUSH PRIVILEGES;" >> /init.sql


# コンテナが終了しないように無限ループ
#tail -f /dev/null
