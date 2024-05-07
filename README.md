# ft_transcendence

dockerの起動方法

 sudo make up
 
 で、nginx, djanngo, postgreSQLのコンテナがbuildされて起動する

 sudo docker exec -it django4242 bash

 でdjangoのコンテナに入って

 python manage.py runserver 0.0.0.0:8000

 を実行してください
 
 ブラウザで
 
 localhost
 
 にアクセスすると、nginxがアクセスをdjangoに投げる

 src/data/django 

 ディレクトリの中を編集していけば、
 
 自動的にdjangoの開発サーバーが再起動されます

 最終的に提出するときは、djangoフォルダをtarにしておいて
 
 dockerfileでtarをappに展開すればいい
