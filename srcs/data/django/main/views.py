from django.shortcuts import render
from django.http import JsonResponse
#from django.views.decorators.csrf import csrf_exempt
import json

def index(request):
    return render(request, 'index.html')
def page1(request):
    return render(request, 'page1.html')
def page2(request):
    return render(request, 'page2.html')
def page3(request):
    return render(request, 'page3.html')
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
            elif page == 'page15':
                response_data = {
                    'content': 'page15',
                }
            else:
                param1 = post_data.get('param1')
                param2 = post_data.get('param2')
                # データ処理ロジックをここに追加
                response_data = {
                    'message': 'Data received and processed successfully',
                    'param1': param1,
                    'param2': param2,
                    'content':page,
                    'page': page,
                    'title': title,
                }



            return JsonResponse(response_data)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
    else:
        return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)

