import json
import asyncio
#from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer

# グローバル変数としてボールの位置と速度を設定
ball_x = 0
ball_y = 0
ball_speed_x = 40
ball_speed_y = 40
player1_x = 3800
player1_y = 0
player2_x = -3800
player2_y = 0

player1_length = 600
player2_length = 600
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
        global ball_x, ball_y, ball_speed_x, ball_speed_y, player1_y, player2_y, score_player1, score_player2
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        if message == 'update_position':
             
            tmp1 = text_data_json['player1_y']
            if tmp1 != "":
                if tmp1 > MAX_Y - player1_length / 2:
                    tmp1 = MAX_Y - player1_length / 2
                elif tmp1 < MIN_Y + player1_length / 2:
                    tmp1 = MIN_Y + player1_length / 2
                player1_y = tmp1
            tmp2 = text_data_json['player2_y']
            if tmp2 != "":
                if tmp2 > MAX_Y - player2_length / 2:
                    tmp2 = MAX_Y - player2_length / 2
                elif tmp2  < MIN_Y + player2_length / 2:
                    tmp2 = MIN_Y + player2_length / 2
                player2_y = tmp2


            # ロジックを実装してプレイヤー1の位置を更新
            # ここにプレイヤー2やボールの位置、スコアの更新などのロジックを追加            

            # game_state = {
            #     'info': "paddle",
            #     'player1_y': player1_y,
            #     'player2_y': player2_y,
            # }

            # await self.channel_layer.group_send(
            #     "main",
            #     {
            #         "type": "game_update",
            #         "game_state": game_state,
            #     }
            # )
 

    async def update_ball_position(self):
        global ball_x, ball_y, ball_speed_x, ball_speed_y, player1_y, player2_y, score_player1, score_player2

        while True:
            # ボールが上下の壁に当たった場合、Y方向の速度を反転
            if ball_y >= MAX_Y or ball_y <= MIN_Y:
                ball_speed_y *= -1

            # ボールが左右の壁に当たった場合、ゲームオーバーとして適切な処理を行うか、
            # 速度を反転して反射させる
            if ball_x >= MAX_X:
                ball_speed_x *= -1
            elif ball_x <= MIN_X:
                ball_speed_x *= -1
            
            if ball_x >= player1_x and ball_x <= plyaer1_x + 10 and ball_y > player1_y - player1_length / 2 and ball_y < player1_y + player1_length / 2:
                ball_speed_x *= -1
            elif ball_x <= player2_x and ball_x >= player2_x - 10 and ball_y > player2_y - player2_length / 2 and ball_y < player2_y + player2_length / 2:
                ball_speed_x *= -1

            # ボールの位置を更新
            ball_x += ball_speed_x
            ball_y += ball_speed_y

            game_state = {
                'info':'all',
                'player1_y': player1_y,
                'player2_y': player2_y,
                'ball_x': ball_x,   
                'ball_y': ball_y,   
                'score_player1': 0,
                'score_player2': 0,
            }

            # ゲームの状態をクライアントに送信
            await self.channel_layer.group_send(         
                "main",
                {
                    "type": "game_update",
                    "game_state": game_state
                }
            #    await self.send_game_state(game_state)
            )
            # 一定の間隔でボールの位置を更新（例えば0.1秒）
            await asyncio.sleep(0.033)

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