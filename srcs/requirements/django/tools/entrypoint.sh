#!/bin/bash

set -e 

# エントリーポイントスクリプト (entrypoint.sh)
# データベースマイグレーションの適用
python manage.py migrate

# 静的ファイルの収集
#python manage.py collectstatic --noinput

# サーバーの起動
# gunicornでWSGIサーバーをバックグラウンドで起動
#gunicorn main.wsgi:application --bind 0.0.0.0:8000 &

# daphneでASGIサーバーを起動

#python /createsuperuser.py
python manage.py runserver 0.0.0.0:8000 &


exec daphne -b 0.0.0.0 -p 8001 team_my2.asgi:application

