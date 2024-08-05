FROM python:3.9

# 作業ディレクトリを設定
WORKDIR /app

# 依存関係をインストール
COPY    ./conf/requirements.txt /app
RUN     pip install --upgrade pip
RUN     pip install --no-cache-dir -r requirements.txt

RUN     pip install Pillow
RUN     pip install channels
RUN     pip install channels-redis
RUN     pip install django-redis
RUN     pip install aioredis

RUN     pip install daphne
RUN     pip install gunicorn
RUN     pip install psycopg2-binary


EXPOSE  8000 8001

#CMD  ["python", "manage.py", "makemigrations"]
#CMD  ["python", "manage.py", "migrate"]

#COPY toosl/entrypoint.sh /entrypoint.sh
#RUN chmod +x /entrypoint.sh
#CMD  ["python", "./tools/createsuperuser.py"]
    
# Djangoアプリケーションの開発サーバーを起動
#CMD ["python", "manage.py", "runserver", "0.0.0.0:8000", "--noreload"]
#CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
#CMD ["tail",  "-f", "/dev/null"]
COPY ./tools/createsuperuser.py /createsuperuser.py
RUN chmod +x /createsuperuser.py

COPY ./tools/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
