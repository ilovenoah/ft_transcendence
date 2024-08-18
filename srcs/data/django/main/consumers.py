import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'team_my2.settings')
django.setup()

import json
import math
import time
import asyncio
import aioredis
import random
#from channels.generic.websocket import WebsocketConsumer
from channels.generic.websocket import AsyncWebsocketConsumer
from django_redis import get_redis_connection
from asgiref.sync import sync_to_async  # sync_to_asyncをインポート

from channels.db import database_sync_to_async

from django.db import models
from .models import Matchmaking
import logging


# logger = logging.getLogger(__name__)
logger = logging.getLogger('main')


#コートの大きさ
MAX_X = 4000
MIN_X = -4000
MAX_Y = 2000
MIN_Y = -2000

#当たり判定のマージン
HIT_MARGIN = 10 

#1秒間に何回表示するか
interval = 1 / 60.0

animate_interval = 1000 / 60.0

#点数が入ったときに何秒間停止するか
sleep_sec = 3.0

 
class PongConsumer(AsyncWebsocketConsumer):
    room_tasks = {}

    async def connect(self):
 # self.room_name = "main"
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'pong_{self.room_name}'
        # first_flag = True

        self.match = await sync_to_async(self.get_match)()
        # logger.debug(match.user1_id)
        user = self.scope["user"]
        # ユーザーが認証されているかどうかを確認
        if user.is_authenticated:
            self.user1 =  self.match.user1_id
            self.user2 =  self.match.user2_id
            self.user3 =  self.match.user3_id
            self.user4 =  self.match.user4_id

            self.single = self.match.is_single
            self.doubles = self.match.doubles_id
   
            self.lasttime = 0
            self.aistrength = 0.6

            if self.match.user2_id is None and self.match.is_single is False :
                self.user2 = user.id
                self.match.user2_id = user.id
                await sync_to_async(self.match.save()) 
     

        # aioredisを使ってRedisに接続
        # self.redis = await aioredis.create_redis_pool('redis://redis4242')

        self.redis = await aioredis.from_url('redis://redis4242:6379')


        # Redisから状態を取得
        game_state_raw = await self.redis.get(self.room_group_name)

        self.memory = []

        if game_state_raw:
            self.game_state = json.loads(game_state_raw)

        elif self.doubles is None:
            self.game_state = {
                'ball': [0, 0, 70, math.pi / 4.0], # x, y , speed, angle
                'paddle_1':[3800, 0, 600], # x, y, length
                'paddle_2':[-3800, 0, 600],
                'scores':[0, 0],
                'count_sleep': 0,
                'user_status':[0,0,0,0,0],
           }
        else :
            self.game_state = {
                'ball': [0, 0, 70, math.pi / 4.0], # x, y , speed, angle
                'paddle_1':[3800, 0, 600], # x, y, length
                'paddle_2':[-3800, 0, 600],
                'paddle_3':[1800, 0, 600], # x, y, length
                'paddle_4':[-1800, 0, 600],
                'scores':[0, 0],
                'count_sleep': 0,
                'user_status':[0,0,0,0,0],
           }

        #パドルサイズ
        if self.match.paddle_size == 1 :
            self.game_state['paddle_1'][2] = 400
            self.game_state['paddle_2'][2] = 400
            if self.doubles is not None:
                self.game_state['paddle_3'][2] = 400
                self.game_state['paddle_4'][2] = 400
        elif self.match.paddle_size == 2 :
            self.game_state['paddle_1'][2] = 600
            self.game_state['paddle_2'][2] = 600
            if self.doubles is not None:
                self.game_state['paddle_3'][2] = 600
                self.game_state['paddle_4'][2] = 600
        elif self.match.paddle_size == 3 :
            self.game_state['paddle_1'][2] = 800
            self.game_state['paddle_2'][2] = 800
            if self.doubles is not None:
                self.game_state['paddle_3'][2] = 800
                self.game_state['paddle_4'][2] = 800
    
        #ボールスピード
        if self.match.ball_speed == 1 :
            self.game_state['ball'][2] = 50
        elif self.match.ball_speed == 2 :
            self.game_state['ball'][2] = 70
        elif self.match.ball_speed == 3 :
            self.game_state['ball'][2] = 100

        #マッチポイント
        self.game_state['match_point'] = self.match.match_point

        #aiの強さ
        if self.match.ai ==  1:
            self.aistrength = 0.4
        elif self.match.ai ==  2:
            self.aistrength = 0.6
        elif self.match.ai ==  3:
            self.aistrength = 0.8

    

        if self.single is True :
            self.game_state['user_status'][2] = 1

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

        # ボールの位置を定期的に更新する非同期タスクを開始
               
        if self.room_group_name not in PongConsumer.room_tasks or PongConsumer.room_tasks[self.room_group_name].done():
            PongConsumer.room_tasks[self.room_group_name] = asyncio.create_task(self.update_ball_position())



        # 接続されたクライアントに現在のゲーム状態を送信
        await self.send(text_data=json.dumps(self.game_state))

    async def disconnect(self, close_code):
        await self.redis.set(self.room_group_name, json.dumps(self.game_state)) 
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        # タスクをキャンセル
        # self.update_task.cancel()
        # Redis接続を閉じる
        await self.redis.close()
        await self.redis.wait_closed()

    async def server_disconnect(self):
        await self.close()

    async def disconnect_after_delay(consumer):
        await asyncio.sleep(5)
        await consumer.server_disconnect()


    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        user = self.scope["user"]


        if message == 'update_position':
            # if self.user1 == user.id :

            if 'player1_y' in text_data_json:
                tmp1 = text_data_json['player1_y']
                if tmp1 != "":
                    if tmp1 > MAX_Y :
                        tmp1 = MAX_Y
                        # tmp1 = MAX_Y - self.game_state['paddle_1'][2] / 10
                    elif tmp1 < MIN_Y:
                        tmp1 = MIN_Y
                        # tmp1 = MAX_Y + self.game_state['paddle_1'][2] / 10
                    self.game_state['paddle_1'][1] = tmp1
            # elif self.user2 == user.id :
            if 'player2_y' in text_data_json:
                tmp2 = text_data_json['player2_y']
                if tmp2 != "":
                    if tmp2 > MAX_Y :
                        tmp2 = MAX_Y
                    elif tmp2 < MIN_Y :
                        tmp2 = MIN_Y 
                    self.game_state['paddle_2'][1] = tmp2
            # elif self.user3 == user.id :
            if 'player3_y' in text_data_json:
                tmp3 = text_data_json['player3_y']
                if tmp3 != "":
                    if tmp3 > MAX_Y :
                        tmp3 = MAX_Y
                    elif tmp3 < MIN_Y :
                        tmp3 = MIN_Y 
                    self.game_state['paddle_3'][1] = tmp3
            # elif self.user4 == user.id :
            if 'player4_y' in text_data_json:
                tmp4 = text_data_json['player4_y']
                if tmp4 != "":
                    if tmp4 > MAX_Y :
                        tmp4 = MAX_Y
                    elif tmp4 < MIN_Y :
                        tmp4 = MIN_Y 
                    self.game_state['paddle_4'][1] = tmp4



        elif message == 'ready_state' :
            # logger.debug(f'ユーザーID: {user.id}')
            # logger.debug(f'11: {self.user1}')
            # logger.debug(f'22: {self.user2}')
            # logger.debug(f'dd: {self.doubles}')

            if self.user1 == user.id :
                self.game_state['user_status'][1] = 1
            elif self.user2 == user.id :
                self.game_state['user_status'][2] = 1
            elif self.user3 == user.id :
                self.game_state['user_status'][3] = 1
            elif self.user4 == user.id :
                self.game_state['user_status'][4] = 1


            if self.doubles is None :
                if self.game_state['user_status'][1] == 1 and self.game_state['user_status'][2] == 1:
                    self.game_state['user_status'][0] = 1
            else:
                if self.game_state['user_status'][1] == 1 and self.game_state['user_status'][2] == 1 and  self.game_state['user_status'][3] == 1 and self.game_state['user_status'][4] == 1:
                    self.game_state['user_status'][0] = 1


            
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
        global sleep_sec, interval
        try:
            while True:
                if self.game_state['user_status'][0] == 1 and self.game_state['count_sleep'] > 0 :
                    self.game_state['count_sleep'] -= interval
                    self.game_state['ball'][0] = 0
                    self.game_state['ball'][1] = 0
                elif self.game_state['user_status'][0] == 1 :
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
                        elif self.game_state['ball'][1] < self.game_state['paddle_1'][1] + self.game_state['paddle_1'][2] / 2 + HIT_MARGIN and self.game_state['ball'][1] > self.game_state['paddle_1'][1] - self.game_state['paddle_1'][2] / 2 - HIT_MARGIN:
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
                        elif self.game_state['ball'][1] < self.game_state['paddle_2'][1] + self.game_state['paddle_2'][2] / 2 + HIT_MARGIN and self.game_state['ball'][1] > self.game_state['paddle_2'][1] - self.game_state['paddle_2'][2] / 2 - HIT_MARGIN:
                            self.game_state['ball'][3] = math.pi - self.game_state['ball'][3]
                    #ダブルスのとき パドルが４つあるときの対応
                    if self.doubles is not None :
                        if self.game_state['ball'][0] >= self.game_state['paddle_3'][0] and self.game_state['ball'][0] <= self.game_state['paddle_3'][0] + 100:
                            if self.game_state['ball'][1] > self.game_state['paddle_3'][1] + self.game_state['paddle_3'][2] / 5 * 2 and self.game_state['ball'][1] <= self.game_state['paddle_3'][1] + self.game_state['paddle_3'][2] / 2:
                                self.game_state['ball'][3] = math.pi / 3 * 2
                            elif self.game_state['ball'][1] > self.game_state['paddle_3'][1] + self.game_state['paddle_3'][2] / 5 and self.game_state['ball'][1] < self.game_state['paddle_3'][1] + self.game_state['paddle_3'][2] / 5 * 2:
                                self.game_state['ball'][3] = math.pi / 4 * 3
                            elif self.game_state['ball'][1] < self.game_state['paddle_3'][1] - self.game_state['paddle_3'][2] / 5 and self.game_state['ball'][1] > self.game_state['paddle_3'][1] - self.game_state['paddle_3'][2] / 5 * 2:
                                self.game_state['ball'][3] = math.pi / 4 * 5
                            elif self.game_state['ball'][1] < self.game_state['paddle_3'][1] - self.game_state['paddle_3'][2] / 5 * 2 and self.game_state['ball'][1] > self.game_state['paddle_3'][1] - self.game_state['paddle_3'][2] / 2:
                                self.game_state['ball'][3] = math.pi / 3 * 4
                            elif self.game_state['ball'][1] < self.game_state['paddle_3'][1] + self.game_state['paddle_3'][2] / 2 + HIT_MARGIN and self.game_state['ball'][1] > self.game_state['paddle_3'][1] - self.game_state['paddle_3'][2] / 2  - HIT_MARGIN:
                                self.game_state['ball'][3] = math.pi - self.game_state['ball'][3]
                        elif self.game_state['ball'][0] <= self.game_state['paddle_4'][0] and self.game_state['ball'][0] >= self.game_state['paddle_4'][0] - 100:
                            if self.game_state['ball'][1] > self.game_state['paddle_4'][1] + self.game_state['paddle_4'][2] / 5 * 2 and self.game_state['ball'][1] <= self.game_state['paddle_4'][1] + self.game_state['paddle_4'][2] / 2:
                                self.game_state['ball'][3] = math.pi / 3 
                            elif  self.game_state['ball'][1] > self.game_state['paddle_4'][1] + self.game_state['paddle_4'][2] / 5 and self.game_state['ball'][1] < self.game_state['paddle_4'][1] + self.game_state['paddle_4'][2] / 5 * 2:
                                self.game_state['ball'][3] = math.pi / 4    
                            elif self.game_state['ball'][1] < self.game_state['paddle_4'][1] - self.game_state['paddle_4'][2] / 5 and self.game_state['ball'][1] > self.game_state['paddle_4'][1] - self.game_state['paddle_4'][2] / 5 * 2:
                                self.game_state['ball'][3] = math.pi / 4 * 7
                            elif self.game_state['ball'][1] < self.game_state['paddle_4'][1] - self.game_state['paddle_4'][2] / 5 * 2 and self.game_state['ball'][1] > self.game_state['paddle_4'][1] - self.game_state['paddle_4'][2] / 2:
                                self.game_state['ball'][3] = math.pi / 3 * 5
                            elif self.game_state['ball'][1] < self.game_state['paddle_4'][1] + self.game_state['paddle_4'][2] / 2  + HIT_MARGIN and self.game_state['ball'][1] > self.game_state['paddle_4'][1] - self.game_state['paddle_4'][2] / 2 - HIT_MARGIN:
                                self.game_state['ball'][3] = math.pi - self.game_state['ball'][3]
                      

                self.game_state['info'] = 'all'

                #AIブロック
                if self.single is True :
                    currenttime = time.time() * 1000
                    deltatime = currenttime - self.lasttime
                    if deltatime > animate_interval:
                        self.lasttime = currenttime - (deltatime % animate_interval)
                         # ランダム性を導入
                        # if random.random() < 0.6:
                        #     self.game_state['paddle_2'][1] += random.randint(-100, 100)
                        # シンプルな追尾アルゴリズム
                        if self.game_state['ball'][1] > self.game_state['paddle_2'][1]:
                            if random.random() < self.aistrength:
                                self.game_state['paddle_2'][1] += min(100, self.game_state['ball'][1] - self.game_state['paddle_2'][1])
                        elif self.game_state['ball'][1] < self.game_state['paddle_2'][1]:
                            if random.random() < self.aistrength:
                                self.game_state['paddle_2'][1] -= min(100, - self.game_state['ball'][1] + self.game_state['paddle_2'][1])

                    #別のアルゴリズム
                    # 過去のボール位置を記憶
                    # self.memory.append(self.game_state['ball'][1])
                    # if len(self.memory) > 1000:  # メモリの長さを制限
                    #     self.memory.pop(0)        
                    # # パターンを検出して動く
                    # if len(set(self.memory)) == 1:  # 全て同じ位置ならそこに移動
                    #         target_y = self.memory[0]
                    # else:
                    #     target_y = self.game_state['ball'][1]
                    # if target_y > self.game_state['paddle_2'][1]:
                    #         self.game_state['paddle_2'][1] += min(50, target_y - self.game_state['paddle_2'][1])
                    # elif target_y < self.game_state['paddle_2'][1]:
                    #     self.game_state['paddle_2'][1] -= min(50, self.game_state['paddle_2'][1] - target_y)
                    # ボールの未来の位置を予測
                    # predicted_y = self.game_state['ball'][1] + math.sin(self.game_state['ball'][2]) * (self.game_state['paddle_2'][0] - self.game_state['ball'][0]) / math.cos(self.game_state['ball'][2])
                    # if     predicted_y > self.game_state['paddle_2'][1]:
                    #     self.game_state['paddle_2'][1] += min(70, predicted_y - self.game_state['paddle_2'][1])
                    #     if self.game_state['paddle_2'][1] > MAX_Y :
                    #         self.game_state['paddle_2'][1] = MAX_Y
                    # elif predicted_y < self.game_state['paddle_2'][1]:
                    #     self.game_state['paddle_2'][1] -= min(70, self.game_state['paddle_2'][1] - predicted_y)
                    #     if self.game_state['paddle_2'][1] < MIN_Y :
                    #         self.game_state['paddle_2'][1] = MIN_Y


                if self.game_state['scores'][0] >= self.game_state['match_point']  or self.game_state['scores'][1] >= self.game_state['match_point'] :
                    self.game_state['status'] = 2
    
     
                # ゲームの状態をクライアントに送信
                await self.channel_layer.group_send(         
                    self.room_group_name,
                    {
                        "type": "game_update",
                        "game_state": self.game_state
                    }
                )

                #Dueceを設定
                if self.game_state['scores'][0] == (self.game_state['match_point']  - 1) and self.game_state['scores'][1] == (self.game_state['match_point']  - 1) :
                    self.game_state['match_point']  += 1
                #matchの終了判断
                if self.game_state['scores'][0] >= self.game_state['match_point']  or self.game_state['scores'][1] >= self.game_state['match_point'] :
                    
                    # logger = logger.debug("dango")
                    # logger = logger.debug(self.match.point1)
                   # logger = logger.debug(self.match.point2)

                    # await self.send(text_data=json.dumps({
                    #     'error': 'User not found'
                    # }))

                    self.match.point1 = self.game_state['scores'][0]
                    self.match.point2 = self.game_state['scores'][1]        
                    #シングルプレイ、ダブルスのときはwinnerを設定しない
                    if self.single is True or self.doubles is not None:
                        self.match.point1 = self.game_state['scores'][0]
                    #それ以外のときは、winnerを設定する
                    else:
                        if self.game_state['scores'][0] > self.game_state['scores'][1] :
                            self.match.winner_id = self.user1 
                        else:
                            self.match.winner_id = self.user2 
                    await database_sync_to_async(self.match.save)()  # 非同期で保存
                    # await sync_to_async(self.match.save)()

                    await asyncio.sleep(3600)
                    PongConsumer.room_tasks[self.room_group_name].cancel()
                    asyncio.create_task(disconnect_after_delay(self))

                else:
                    await asyncio.sleep(interval)

                # Redisに状態を保存
                await self.redis.set(self.room_group_name, json.dumps(self.game_state))

        # async def send_game_state(self, game_state):
        #     await self.send(text_data=json.dumps(game_state))
        except Exception as e:
            print(f"Error in update_ball_position: {e}")

    async def game_update(self, event):
        self.game_state = event["game_state"]
        await self.send(text_data=json.dumps(self.game_state))

        # game_state = event['game_state']
        # # クライアントにゲーム状態を送信
        # await self.send(text_data=json.dumps({
        #     'game_state': game_state
        # }))

    def get_match(self):
        # 同期的なDjango ORM操作＿
        return Matchmaking.objects.get(pk=self.room_name)



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