import subprocess

# Djangoのプロジェクトディレクトリに移動する
project_directory = '/app'
command = ['python', 'manage.py', 'createsuperuser']

# subprocessモジュールを使用してコマンドを実行する
process = subprocess.Popen(command, cwd=project_directory, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

# ユーザー名とパスワードの入力
username = "admin"
email = "admin@example.com"
password = "password"

# ユーザー名、メール、パスワードを標準入力に書き込む
input_data = f"{username}\n{email}\n{password}\n"
process.stdin.write(input_data.encode('utf-8'))
process.stdin.flush()

# コマンドの実行結果を取得する
output, error = process.communicate()

if process.returncode == 0:
    print("createsuperuser コマンドが正常に実行されました。")
    print("出力:", output.decode('utf-8'))
else:
    print("createsuperuser コマンドの実行中にエラーが発生しました。")
    print("エラー:", error.decode('utf-8'))