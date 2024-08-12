import json
import math
import asyncio
import aioredis
import random
#from channels.generic.websocket import WebsocketConsumer
from channels.generic.websocket import AsyncWebsocketConsumer
from django_redis import get_redis_connection
from asgiref.sync import sync_to_async  # sync_to_asyncをインポート


import logging



logger = logging.getLogger(__name__)



#マッチスコア
score_match = 10

#コートの大きさ
MAX_X = 4000
MIN_X = -4000
MAX_Y = 2000
MIN_Y = -2000

#1秒間に何回表示するか
interval = 1 / 60.0

#点数が入ったときに何秒間停止するか
sleep_sec = 3.0

 
class PongConsumer(AsyncWebsocketConsumer):
    room_tasks = {}

    async def connect(self):
 # self.room_name = "main"
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'pong_{self.room_name}'
        first_flag = True

        # aioredisを使ってRedisに接続
        # self.redis = await aioredis.create_redis_pool('redis://redis4242')

        self.redis = await aioredis.from_url('redis://redis4242:6379')

        # ログインユーザーの取得
        user = self.scope["user"]        
        # ユーザーが認証されているかどうかを確認
        if user.is_authenticated:
            username = user.username
        else:
            username = ""

        logger.debug(username)

        





        # Redisから状態を取得
        game_state_raw = await self.redis.get(self.room_group_name)

        self.memory = []

        if game_state_raw:
            self.game_state = json.loads(game_state_raw)
            # ゲームの状態をクライアントに送信
            await self.channel_layer.group_send(         
                self.room_group_name,
                {
                    "type": "game_update",
                    "game_state": self.game_state
                }
            #    await self.send_game_state(game_state)
            )   
        else:
            self.game_state = {
                'ball': [0, 0, 70, math.pi / 4.0], # x, y , speed, angle
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

        # self.update_task = asyncio.create_task(self.update_ball_position())
        # if self.room_group_name not in PongConsumer.room_tasks or PongConsumer.room_tasks[self.room_group_name].done():
        PongConsumer.room_tasks[self.room_group_name] = asyncio.create_task(self.update_ball_position())
        

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        # タスクをキャンセル
        # self.update_task.cancel()
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
                if tmp1 > MAX_Y :
                    tmp1 = MAX_Y
                    # tmp1 = MAX_Y - self.game_state['paddle_1'][2] / 10
                elif tmp1 < MIN_Y:
                    tmp1 = MIN_Y
                    # tmp1 = MAX_Y + self.game_state['paddle_1'][2] / 10
                self.game_state['paddle_1'][1] = tmp1
            # tmp2 = text_data_json['player2_y']
            # if tmp2 != "":
            #     if tmp2 > MAX_Y :
            #         tmp2 = MAX_Y
            #     elif tmp2  < MIN_Y :
            #         tmp2 = MIN_Y 
            #     self.game_state['paddle_2'][1] = tmp2


                
            # Redisに状態を保存
            # await self.redis.set(self.room_group_name, json.dumps(self.game_state))

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



            #AIブロック
            #  # ランダム性を導入
            # if random.random() < 0.4:
            #     self.game_state['paddle_2'][1] += random.randint(-300, 300)
            # # シンプルな追尾アルゴリズム
            # if self.game_state['ball'][1] > self.game_state['paddle_2'][1]:
            #     self.game_state['paddle_2'][1] += min(100, self.game_state['ball'][1] - self.game_state['paddle_2'][1])
            # elif self.game_state['ball'][1] < self.game_state['paddle_2'][1]:
            #     self.game_state['paddle_2'][1] -= min(100, - self.game_state['ball'][1] + self.game_state['paddle_2'][1])
           

            # 過去のボール位置を記憶
            self.memory.append(self.game_state['ball'][1])
            if len(self.memory) > 1000:  # メモリの長さを制限
                self.memory.pop(0)
        
            # パターンを検出して動く
            if len(set(self.memory)) == 1:  # 全て同じ位置ならそこに移動
                target_y = self.memory[0]
            else:
                target_y = self.game_state['ball'][1]
        
            if target_y > self.game_state['paddle_2'][1]:
                self.game_state['paddle_2'][1] += min(50, target_y - self.game_state['paddle_2'][1])
            elif target_y < self.game_state['paddle_2'][1]:
                self.game_state['paddle_2'][1] -= min(50, self.game_state['paddle_2'][1] - target_y)



            # ボールの未来の位置を予測
            # predicted_y = self.game_state['ball'][1] + math.sin(self.game_state['ball'][2]) * (self.game_state['paddle_2'][0] - self.game_state['ball'][0]) / math.cos(self.game_state['ball'][2])
            # if predicted_y > self.game_state['paddle_2'][1]:
            #     self.game_state['paddle_2'][1] += min(70, predicted_y - self.game_state['paddle_2'][1])
            #     if self.game_state['paddle_2'][1] > MAX_Y :
            #         self.game_state['paddle_2'][1] = MAX_Y
            # elif predicted_y < self.game_state['paddle_2'][1]:
            #     self.game_state['paddle_2'][1] -= min(70, self.game_state['paddle_2'][1] - predicted_y)
            #     if self.game_state['paddle_2'][1] < MIN_Y :
            #         self.game_state['paddle_2'][1] = MIN_Y



            # ゲームの状態をクライアントに送信
            await self.channel_layer.group_send(         
                self.room_group_name,
                {
                    "type": "game_update",
                    "game_state": self.game_state
                }
            #    await self.send_game_state(game_state)
            )            

            #Dueceを設定
            if self.game_state['scores'][0] == (score_match - 1) and self.game_state['scores'][1] == (score_match - 1) :
                score_match += 1
            #matchの終了判断
            if self.game_state['scores'][0] >= score_match or self.game_state['scores'][1] >= score_match:
                await self.redis.set(self.room_group_name, json.dumps(self.game_state))
                asyncio.create_task(disconnect_after_delay(self))
                PongConsumer.room_tasks[self.room_group_name].cancel()
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


    def ai_move(self):
        # シンプルな追尾アルゴリズム
        # if self.game_state['ball'][1] > self.game_state['paddle_2'][1]:
        #     self.game_state['paddle_2'][1] += min(5, self.game_state['ball'][1] - self.game_state['paddle_2'][1])
        # elif self.game_state['ball'][1] < self.game_state['paddle_2'][1]:
        #     self.game_state['paddle_2'][1] -= min(5, self.game_state['ball'][1] - self.game_state['paddle_2'][1])

        # # ランダム性を導入
        # if random.random() < 0.1:
        #     self.game_state['paddle_2'][1] += random.randint(-10, 10)
        return