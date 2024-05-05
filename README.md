# ft_transcendence

dockerの起動方法

 sudo make up
 
 で、nginx, djanngo, postgreSQLのコンテナがbuildされて起動する
 
 ブラウザで
 
 localhost
 
 にアクセスすると、nginxがアクセスをdjangoに投げる

 src/data/django 

 ディレクトリの中を編集していけば、
 
 自動的にdjangoの開発サーバーが再起動されます

 最終的に提出するときは、djangoフォルダをtarにしておいて
 
 dockerfileでtarをappに展開すればいい

---
Apple M2環境で
sudo make upをすると以下のエラーがでた.
```md
docker:desktop-linux
 => [postgres internal] load build definition from Dockerfile                                                                                                0.0s
 => => transferring dockerfile: 157B                                                                                                                         0.0s
 => ERROR [postgres internal] load metadata for docker.io/library/postgres:16.2                                                                              0.7s
------
 > [postgres internal] load metadata for docker.io/library/postgres:16.2:
------
failed to solve: postgres:16.2: failed to resolve source metadata for docker.io/library/postgres:16.2: error getting credentials - err: exit status 1, out: ``
make: *** [build] Error 17
```

以下を実行することでうまくいくようになった.
```md
$ brew install docker-credential-helper
```

```bash
$ vim ~/.docker/config.json
{   "credsStore": "osxkeychain" }
```

---
Chapter 2
データベースのモデルをPythonで記述することができる.

---
Chapter 3
urlを色々定義できる.
