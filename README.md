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

開発の仕様

 srcs/data/djangoの中でスクリプトを展開します
 
 app名がteam_my2
 
 メインのディレクトリがmainです
 
 基本的にmainの中でファイルを更新していきます
 
 djangoの設定を変えるときは、
 
 team_my2のsettings.pyやurls.pyを変更します
 
アクセス先は、
 
 https://localhost/dev/
 
 
 開発中、djangoを噛ませたくないときは、
 
 srcs/data/nginx
 
 にhtmlなどをおいて、
 
 http://localhost:8080/
 
 にアクセスすればテストできます

 srcs/data/django/main/
 
 では、urls.py,views.pyなどを設定してください
 
 templatesディレクトリの中に基本的なhtmlファイルがおいてあります
 
 global_base.htmlは、spaの基本となるhtmlです
  
 spaの挙動などを変えたいときは、app.jsを改変します。
 
 その他、staticディレクトリにはboostrapのファイルも入っていますが、
 
 静的なファイルはstaticディレクトリに置きます。
 
 呼び出し方は、global_base.htmlを参考にすれば解ると思います。
 

 