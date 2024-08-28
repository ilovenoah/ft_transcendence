# Dockerfile

FROM    debian:bullseye-slim

# 環境変数を設定して、インタラクティブモードのプロンプトを抑制
ENV     DEBIAN_FRONTEND=noninteractive

# 必要なパッケージをインストール
RUN apt update && \
    apt install -y postfix mailutils && \
    apt clean

# Postfixの設定ファイルをコピー
COPY ./conf/main.cf /etc/postfix/main.cf

# Postfixサービスを開始するスクリプトを作成
RUN echo '#!/bin/bash\nservice postfix start\nbash' > /usr/local/bin/start.sh && chmod +x /usr/local/bin/start.sh

# コンテナ起動時にPostfixを起動
#CMD ["/usr/local/bin/start.sh"]


CMD ["tail",  "-f", "/dev/null"]

