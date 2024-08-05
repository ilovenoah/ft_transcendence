import json
import math
import asyncio
import aioredis
#from channels.generic.websocket import WebsocketConsumer
from channels.generic.websocket import AsyncWebsocketConsumer
from django_redis import get_redis_connection
from asgiref.sync import sync_to_async  # sync_to_asyncをインポート

#マッチスコア
score_match = 10

#コートの大きさ
MAX_X = 4000
MIN_X = -4000
MAX_Y = 2000
MIN_Y = -2000

#1秒間に何回表示するか
interval = 1 / 30.0

#点数が入ったときに何秒間停止するか
sleep_sec = 3.0


class PongConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # self.room_name = "main"


        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'pong_{self.room_name}'

        # aioredisを使ってRedisに接続
        # self.redis = await aioredis.create_redis_pool('redis://redis4242')

        self.redis = await aioredis.from_url('redis://redis4242:6379')

        # Redisから状態を取得
        game_state_raw = await self.redis.get(self.room_group_name)

        if game_state_raw:
            self.game_state = json.loads(game_state_raw)
        else:
            self.game_state = {
                'ball': [0, 0, 50, math.pi / 4.0], # x, y , speed, angle
                'paddle_1':[3800, 0, 600], # x, y, length
                'paddle_2':[-3800, 0, 600],
                'scores':[0, 0],
                'count_sleep': 0,
           }

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
       # ボールの位置を定期的に更新する非同期タスクを開始

        self.update_task = asyncio.create_task(self.update_ball_position())

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        # タスクをキャンセル
        self.update_task.cancel()

        # Redis接続を閉じる
        self.redis.close()
        await self.redis.wait_closed()

    async def server_disconnect(self):
        await self.close()

    async def disconnect_after_delay(consumer):
        await asyncio.sleep(5)
        await consumer.server_disconnect()


    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        if message == 'update_position':             
            tmp1 = text_data_json['player1_y']
            if tmp1 != "":
                if tmp1 > MAX_Y - self.game_state['paddle_1'][2] / 2:
                    tmp1 = MAX_Y - self.game_state['paddle_1'][2] / 2
                elif tmp1 < MIN_Y + self.game_state['paddle_1'][2] / 2:
                    tmp1 = MIN_Y + self.game_state['paddle_1'][2] / 2
                self.game_state['paddle_1'][1] = tmp1
            tmp2 = text_data_json['player2_y']
            if tmp2 != "":
                if tmp2 > MAX_Y - self.game_state['paddle_2'][2] / 2:
                    tmp2 = MAX_Y - self.game_state['paddle_2'][2] / 2
                elif tmp2  < MIN_Y + self.game_state['paddle_2'][2] / 2:
                    tmp2 = MIN_Y + self.game_state['paddle_2'][2] / 2
                self.game_state['paddle_2'][1] = tmp2

            # ロジックを実装してプレイヤー1の位置を更新
            # ここにプレイヤー2やボールの位置、スコアの更新などのロジックを追加            

            # game_state = {
            #     'info': "paddle",
            #     'self.game_state['paddle_1'][1]': self.game_state['paddle_1'][1],
            #     'self.game_state['paddle_2'][1]': self.game_state['paddle_2'][1],
            # }

            # await self.channel_layer.group_send(
            #     "main",
            #     {
            #         "type": "game_update",
            #         "game_state": game_state,
            #     }
            # )
 

    async def update_ball_position(self):
        global score_match, sleep_sec, interval

        while True:
            if self.game_state['count_sleep'] > 0 :
                self.game_state['count_sleep'] -= interval
                self.game_state['ball'][0] = 0
                self.game_state['ball'][1] = 0
            else :
                # ボールの位置を更新
                self.game_state['ball'][0] += self.game_state['ball'][2] * math.cos(self.game_state['ball'][3])
                self.game_state['ball'][1] += self.game_state['ball'][2] * math.sin(self.game_state['ball'][3])

                # ボールが上下の壁に当たった場合、Y方向のアングルを反転
                if self.game_state['ball'][1] >= MAX_Y or self.game_state['ball'][1] <= MIN_Y:
                    self.game_state['ball'][3] = -1 * self.game_state['ball'][3]

                # ボールが左右の壁に当たった場合、ゲームオーバーとして適切な処理を行うか、
                # 速度を反転して反射させる
                if self.game_state['ball'][0] >= MAX_X:
                    # self.game_state['ball'][3] = math.pi - self.game_state['ball'][3]
                    self.game_state['scores'][1] += 1
                    self.game_state['count_sleep'] = sleep_sec
                    self.game_state['ball'][0] = 0
                    self.game_state['ball'][1] = 0
                elif self.game_state['ball'][0] <= MIN_X:
                    # self.game_state['ball'][3] = math.pi - self.game_state['ball'][3]
                    self.game_state['scores'][0] += 1
                    self.game_state['count_sleep'] = sleep_sec
                    self.game_state['ball'][0] = 0
                    self.game_state['ball'][1] = 0
                elif self.game_state['ball'][0] >= self.game_state['paddle_1'][0] and self.game_state['ball'][0] <= self.game_state['paddle_1'][0] + 100:
                    if self.game_state['ball'][1] > self.game_state['paddle_1'][1] + self.game_state['paddle_1'][2] / 5 * 2 and self.game_state['ball'][1] <= self.game_state['paddle_1'][1] + self.game_state['paddle_1'][2] / 2:
                        self.game_state['ball'][3] = math.pi / 3 * 2
                    elif self.game_state['ball'][1] > self.game_state['paddle_1'][1] + self.game_state['paddle_1'][2] / 5 and self.game_state['ball'][1] < self.game_state['paddle_1'][1] + self.game_state['paddle_1'][2] / 5 * 2:
                        self.game_state['ball'][3] = math.pi / 4 * 3
                    elif self.game_state['ball'][1] < self.game_state['paddle_1'][1] - self.game_state['paddle_1'][2] / 5 and self.game_state['ball'][1] > self.game_state['paddle_1'][1] - self.game_state['paddle_1'][2] / 5 * 2:
                        self.game_state['ball'][3] = math.pi / 4 * 5
                    elif self.game_state['ball'][1] < self.game_state['paddle_1'][1] - self.game_state['paddle_1'][2] / 5 * 2 and self.game_state['ball'][1] > self.game_state['paddle_1'][1] - self.game_state['paddle_1'][2] / 2:
                        self.game_state['ball'][3] = math.pi / 3 * 4
                    elif self.game_state['ball'][1] < self.game_state['paddle_1'][1] + self.game_state['paddle_1'][2] / 2 and self.game_state['ball'][1] > self.game_state['paddle_1'][1] - self.game_state['paddle_1'][2] / 2:
                        self.game_state['ball'][3] = math.pi - self.game_state['ball'][3]
                elif self.game_state['ball'][0] <= self.game_state['paddle_2'][0] and self.game_state['ball'][0] >= self.game_state['paddle_2'][0] - 100:
                    if self.game_state['ball'][1] > self.game_state['paddle_2'][1] + self.game_state['paddle_2'][2] / 5 * 2 and self.game_state['ball'][1] <= self.game_state['paddle_2'][1] + self.game_state['paddle_2'][2] / 2:
                        self.game_state['ball'][3] = math.pi / 3 
                    elif  self.game_state['ball'][1] > self.game_state['paddle_2'][1] + self.game_state['paddle_2'][2] / 5 and self.game_state['ball'][1] < self.game_state['paddle_2'][1] + self.game_state['paddle_2'][2] / 5 * 2:
                        self.game_state['ball'][3] = math.pi / 4    
                    elif self.game_state['ball'][1] < self.game_state['paddle_2'][1] - self.game_state['paddle_2'][2] / 5 and self.game_state['ball'][1] > self.game_state['paddle_2'][1] - self.game_state['paddle_2'][2] / 5 * 2:
                        self.game_state['ball'][3] = math.pi / 4 * 7
                    elif self.game_state['ball'][1] < self.game_state['paddle_2'][1] - self.game_state['paddle_2'][2] / 5 * 2 and self.game_state['ball'][1] > self.game_state['paddle_2'][1] - self.game_state['paddle_2'][2] / 2:
                        self.game_state['ball'][3] = math.pi / 3 * 5
                    elif self.game_state['ball'][1] < self.game_state['paddle_2'][1] + self.game_state['paddle_2'][2] / 2 and self.game_state['ball'][1] > self.game_state['paddle_2'][1] - self.game_state['paddle_2'][2] / 2:
                        self.game_state['ball'][3] = math.pi - self.game_state['ball'][3]

            self.game_state['info'] = 'all'

            # ゲームの状態をクライアントに送信
            await self.channel_layer.group_send(         
                self.room_group_name,
                {
                    "type": "game_update",
                    "game_state": self.game_state
                }
            #    await self.send_game_state(game_state)
            )            

            if self.game_state['scores'][0] == (score_match - 1) and self.game_state['scores'][1] == (score_match - 1) :
                score_match += 1

            # 一定の間隔でボールの位置を更新（例えば0.1秒）
            if self.game_state['scores'][0] >= score_match or self.game_state['scores'][1] >= score_match:
                asyncio.create_task(disconnect_after_delay(self))
                # await asyncio.sleep(3600)
            else:
                await asyncio.sleep(interval)

            # Redisに状態を保存
            await self.redis.set(self.room_group_name, json.dumps(self.game_state))

    # async def send_game_state(self, game_state):
    #     await self.send(text_data=json.dumps(game_state))

    async def game_update(self, event):
        # self.game_state = event["game_state"]
        await self.send(text_data=json.dumps(self.game_state))


    # def game_start(self, event):
    #     //ここでゲームスタートの初期設定

    # def ball_update(self, event):
    #     ball.setx(ball.xcor() + self.game_state['ball'][0]_direction)
    #     ball.sety(ball.ycor() + self.game_state['ball'][1]_direction)

    # def ball_collsion(self, evnet):
    #     if ball.ycor() > 29:
    #         ball.sety(29)
    #         self.game_state['ball'][1]_direction = self.game_state['ball'][1]_direction * -1
    #     if ball.ycor() < -29:
    #         ball.sety(-29)
    #         self.game_state['ball'][1]_direction = self.game_state['ball'][1]_direction * -1