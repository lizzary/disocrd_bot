#教程（第一集）：https://www.youtube.com/watch?v=CHbN_gB30Tw
#教程（第二集）：https://www.youtube.com/watch?v=0lhYddc5M9w

import discord
import os
import json
import sys
import threading
from package.api.deepseek import Deepseek
from package.api.prompt import Prompt
from package.response import Response

class Client(discord.Client):
    def __init__(self,intents:discord.Intents,generate_new_cache:bool = False):
        """

        :param intents:
        :param generate_new_cache: 若为True，则会预先生成10条回复用作缓存
        """
        super().__init__(intents=intents)
        self.config = self.__loadConfig() #注意：该self.config是全局的，只会在机器人程序停止时销毁

        if generate_new_cache:
            print("启动前准备：正在预生成缓存...")
            threads = []
            for i in range(10):
                thread = threading.Thread(target=self.__generate_response_cache_thread,args=("something",Prompt().prompt_block_complex_response,1.5))
                threads.append(thread)
                thread.start()
            for thread in threads:
                thread.join()
            print(self.config)

    def __loadConfig(self):
        config_path = 'config.json'
        with open(config_path, 'r', encoding='utf-8') as config_file:
            config = json.load(config_file)
        return config

    def __generate_response_cache_thread(self,content:str,prompt:Prompt,temperature:float):
        ds = Deepseek(self.config)
        r = ds.tryToGetResponse(content, prompt, temperature)
        print(r)
        self.config["response_cache"]["tease"].append(r)

    async def on_ready(self):
        """
        继承：当机器人启动事件触发，会异步调用该函数
        :return:None
        """
        print(f"一个discord机器人服务已登陆于{self.user}!")

    async def on_message(self,message:discord.Message):
        """
        继承：当有人在机器人所在的群聊发出信息时，会异步调用该函数并传入参数message
        :param message: 一个Message实例
        :return:None
        """
        print(f'来自{message.author}的信息: {message.content}')
        #避免自指
        if message.author == self.user:
            return

        #发送消息
        await message.channel.send(message.author.mention + " hollow #" +str(message.author.id))
        response = Response(self.config,self)
        await response.getResponse(message)

    async def on_member_join(self, member: discord.Member):
        """
        继承：当加入机器人所在的群聊时，会异步调用该函数并传入参数member
        :param member:
        :return:
        """
        # 获取成员加入的服务器的第一个文本频道
        channel = discord.utils.get(member.guild.text_channels)
        if channel:
            await channel.send(f'欢迎 {member.mention} 加入群聊!')

    async def on_voice_state_update(self,member, before, after):
        """
        当语音频道只有机器人时退出语音频道
        :param member:
        :param before:
        :param after:
        :return:
        """
        vc = member.guild.voice_client

        if vc and not vc.is_playing() and len(vc.channel.members) == 1:
            await vc.disconnect()
        return


#导入discord开发者平台中的 "Privileged Gateway Intents" 设置
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.voice_states = True

# 启动
TOKEN = 'something'
client = Client(intents=intents,generate_new_cache=False)
client.run(token=TOKEN)
