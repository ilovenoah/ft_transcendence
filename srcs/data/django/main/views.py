from django.shortcuts import render
from django.http import JsonResponse
#from django.views.decorators.csrf import csrf_exempt
import json
import os

def index(request):
    return render(request, 'index.html')
def ponggame(request):
    return render(request, 'ponggame.html')



def process_post_data(request):
    if request.method == 'POST':
        try:
            post_data = json.loads(request.body)
            page = post_data.get('page')   
            title = post_data.get('title')   
            if page == 'index':
                response_data = {
                    'content': 'index',
                }
            elif page == 'page3':
                response_data = {
                    'content': 'ここにどうやって記述するつもりなだろうか<br>どうしてそうなるのか',
                }
            else:
                param1 = post_data.get('param1')
                param2 = post_data.get('param2')
                # データ処理ロジックをここに追加


                response_data = {
                    'message': 'Data received and processed successfully',
                    'param1': param1,
                    'param2': param2,
                    #'content':page,
                    'content':read_file("page1.html"),
                    'page': page,
                    'title': title,
                }

            return JsonResponse(response_data)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
    else:
        return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)

#関数　ファイルを指定すると内容を返す


def read_file(filename):

    # プロジェクトのベースディレクトリを取得
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # ファイルのパスを構築
    file_path = os.path.join(base_dir, 'main/templates', filename)
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        return content
    except FileNotFoundError:
        return "Error: File not found."
    except Exception as e:
        return f"Error: {e}"