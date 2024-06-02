import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync

class PongConsumer(WebsocketConsumer):
   def connect(self):
        self.accept()
        async_to_sync(self.channel_layer.group_add)("main", self.channel_name)

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)("main", self.channel_name)

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        if message == 'update_position':
            player1_y = text_data_json['player1_y']
            player2_y = text_data_json['player2_y']
            # ロジックを実装してプレイヤー1の位置を更新
            # ここにプレイヤー2やボールの位置、スコアの更新などのロジックを追加
            




            game_state = {
                'player1_y': player1_y,
                'player2_y': 100,  # サンプルデータ
                'ball_x': 400,     # サンプルデータ
                'ball_y':   300,     # サンプルデータ
                'score_player1': 0,  # サンプルデータ
                'score_player2': 0   # サンプルデータ
            }

            async_to_sync(self.channel_layer.group_send)(
                "game",
                {
                    "type": "game_update",
                    "game_state": game_state
                }
            )

    def game_update(self, event):
        game_state = event["game_state"]
        self.send(text_data=json.dumps(game_state))