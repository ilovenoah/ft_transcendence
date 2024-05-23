FROM python:3.9

# 作業ディレクトリを設定
WORKDIR /app

# 依存関係をインストール
COPY    ./conf/requirements.txt /app
RUN     pip install --upgrade pip
RUN     pip install --no-cache-dir -r requirements.txt
RUN     pip install Pillow
#RUN     python -m pip install django
#RUN     pip install django

EXPOSE  8000


# Djangoアプリケーションの開発サーバーを起動
#CMD ["python", "manage.py", "runserver", "0.0.0.0:8000", "--noreload"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
#CMD ["tail",  "-f", "/dev/null"]