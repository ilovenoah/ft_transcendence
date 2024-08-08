FROM python:3.9

# 作業ディレクトリを設定
WORKDIR /app

RUN apt-get update && apt-get install -y gettext

# 依存関係をインストール
COPY    ./conf/requirements.txt /app
RUN     pip install --upgrade pip
RUN     pip install --no-cache-dir -r requirements.txt

RUN     pip install Pillow

EXPOSE  8000

# CMD  ["python", "manage.py", "makemigrations"]
# CMD  ["python", "manage.py", "migrate"]

# CMD  ["python", "./tools/createsuperuser.py"]

# RUN python manage.py makemessages -l ja -l en


# Djangoアプリケーションの開発サーバーを起動
#CMD ["python", "manage.py", "runserver", "0.0.0.0:8000", "--noreload"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
#CMD ["tail",  "-f", "/dev/null"]

