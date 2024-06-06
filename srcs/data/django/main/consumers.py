import json
import asyncio
#from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer

# グローバル変数としてボールの位置と速度を設定
ball_x = 0
ball_y = 0
ball_speed_x = 100
ball_speed_y = 100
player1_y = 0
player2_y = 0
score_player1 = 0
score_player2 = 0
MAX_X = 4000
MIN_X = -4000
MAX_Y = 2000
MIN_Y = -2000



class PongConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("main", self.channel_name)
        await self.accept()
        # ボールの位置を定期的に更新する非同期タスクを開始
        self.update_task = asyncio.create_task(self.update_ball_position())


    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("main", self.channel_name)
        
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        if message == 'update_position':
            player1_y = text_data_json['player1_y']
            player2_y = text_data_json['player2_y']
            # ロジックを実装してプレイヤー1の位置を更新
            # ここにプレイヤー2やボールの位置、スコアの更新などのロジックを追加            


            game_state = {
                'player1_y': player1_y,
                'player2_y': player2_y,
                'ball_x': ball_x,   
                'ball_y': ball_y,   
                'score_player1': 0,
                'score_player2': 0,
            }

            await self.channel_layer.group_send(
                "main",
                {
                    "type": "game_update",
                    "game_state": game_state
                }
            )
 

    async def update_ball_position(self):
        global ball_x, ball_y, ball_speed_x, ball_speed_y, player1_y, player2_y, score_player1, score_player2

        while True:
            # ボールの位置を更新
            ball_x += ball_speed_x
            ball_y += ball_speed_y

            # ボールが上下の壁に当たった場合、Y方向の速度を反転
            if ball_y >= MAX_Y or ball_y <= MIN_Y:
                ball_speed_y *= -1

            # ボールが左右の壁に当たった場合、ゲームオーバーとして適切な処理を行うか、
            # 速度を反転して反射させる
            if ball_x >= MAX_X or ball_x <= MIN_X:
                ball_speed_x *= -1


            game_state = {
                'ball_x': ball_x,
                'ball_y': ball_y,
            }            
            # ゲームの状態をクライアントに送信
            await self.channel_layer.group_send(         
                "main",
                {
                    "type": "game_update",
                    "game_state": game_state
                }
    #            await self.send_game_state(game_state)
            )
            # 一定の間隔でボールの位置を更新（例えば0.1秒）
            await asyncio.sleep(0.3)

    async def send_game_state(self, game_state):
        await self.send(text_data=json.dumps(game_state))

    async def game_update(self, event):
        game_state = event["game_state"]
        await self.send(text_data=json.dumps(game_state))


    # def game_start(self, event):
    #     //ここでゲームスタートの初期設定

    # def ball_update(self, event):
    #     ball.setx(ball.xcor() + ball_x_direction)
    #     ball.sety(ball.ycor() + ball_y_direction)

    # def ball_collsion(self, evnet):
    #     if ball.ycor() > 29:
    #         ball.sety(29)
    #         ball_y_direction = ball_y_direction * -1
    #     if ball.ycor() < -29:
    #         ball.sety(-29)
    #         ball_y_direction = ball_y_direction * -1