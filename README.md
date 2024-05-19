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
 今は、urls.pyで
 path("dev/", include("main.urls")),
 のとおり、dev/を設定しているので、
 アクセス先は、
 https://localhost/dev/
 になりますが、提出時は、
 path("", include("main.urls")),
 にすれば、
 https://localhost/
 になります
 開発中、djangoを噛ませたくないときは、
 srcs/data/nginx
 にhtmlなどをおいて、
 http://localhost:8080/
 にアクセスすればテストできます

 srcs/data/django/main/
 では、urls.py,views.pyなどを設定してください
 templatesディレクトリの中に基本的なhtmlファイルがおいてあります
 global_base.htmlは、spaの基本となるhtmlです
 はじめは、index.htmlが呼び出されますが、
 index.htmlの中を見てください。
 htmlのタグは入っていません。
 その変わり、global_base.htmlが読み込まれ、
 その中に各種情報を挿入して最終的なhtmlが出来上がることになります
 また、index.htmlのなかのリンクをクリックすると、
 page1.htmlなどがid=contentのタグ内に書き換えられます
 page1.htmlの中身も、index.htmlと類似して、
 content_base.html
 をロードして、その中に各種情報を挿入しています。
 そして、出来上がったpage1.htmlを読み込んで、
 index.htmlの中身を書き換えることで、spaを実現します。
 とりあえずは、この４つのファイルを眺めていれば、
 どんなファイルを作っていけばいいか解ると思います。
 これらの操作を行っているのが
 staticディレクトリ内のapp.jsです
 spaの挙動などを変えたいときは、app.jsを改変します。
 その他、staticディレクトリにはboostrapのファイルも入っていますが、
 静的なファイルはstaticディレクトリに置きます。
 呼び出し方は、global_base.htmlを参考にすれば解ると思います。
 

 プルリク出すのでレビューしてください
 sudo make up
 してください
 postgresが立ち上がらない場合は、
 sudo make down
 sudo rm -fr srcs/data/postgres/
 mkdir -p srcs/data/postgres/
 sudo make up

 https://localhost/dev/
 にアクセスして 
 各リンクをクリックして、
 アドレスバーは不変なのに、表示内容とtitleが変わる。
 ブラウザのバックボタンや進むボタンで表示内容、titleが変わる。
 バックボタンや進むボタン長押し？で履歴が表示される

 ファイルやディレクトリの構造などは、readme.mdに書いてあるので参照してください。
 page1,page2,page3,ponggameは今回のレビュー用のサンプルなので、
 みんなが書き方がわかってきたら削除します。

 一応bootstrapも導入したつもりだけど、動作確認などはしていません
 これは今回のレビューの対象ではなく、
 bootstrapを実際に使う際に担当のひとがうまくやってください


