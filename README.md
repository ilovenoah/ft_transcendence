# ft_transcendence

dockerの起動方法

 sudo make up
で、nginx, djanngo, postgreSQLのコンテナがbuildされて起動する

 sudo docker cp app django4242:/
で、appフォルダのファイル群をdjango4242コンテナの/appにコピーする

 sudo docker exec -it django4242 bash
で、djangoコンテナに入って

 python manage.py runserver nginx:8000
で、djangoの開発用サーバーを起動する

ブラウザで
localhost
にアクセスすると、nginxがアクセスをdjangoに投げる

最終的に提出するときは、djangoフォルダをtarにしておいて、
dockerfileでtarをappに展開すればいい
